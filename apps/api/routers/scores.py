from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta, datetime
import numpy as np
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/scores",
    tags=["Facility Scores Ranking"]
)

# Computes scores for the past 30 days
def compute_scores_for_all(db: Session, district: str = "Lucknow"):
    today = date.today()
    start_date = today - timedelta(days=30)
    facilities = db.query(models.Facility).filter(models.Facility.district == district).all()
    
    scores_updated = 0
    
    for f in facilities:
        # 1. Stock Reliability (30% weight)
        # Count days with critical low stock or stockouts
        skus = db.query(models.StockItem).filter(models.StockItem.facility_id == f.facility_id).all()
        stockouts = sum(1 for s in skus if s.quantity == 0)
        low_stock = sum(1 for s in skus if s.quantity < s.min_threshold)
        
        # Simple deduction formula
        stock_score = 100.0 - (stockouts * 15.0) - (low_stock * 2.0)
        stock_score = max(0.0, min(100.0, stock_score))
        
        # 2. Attendance Rate (25% weight)
        total_scheduled = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.facility_id == f.facility_id,
            models.AttendanceRecord.attendance_date >= start_date
        ).count()
        
        total_present = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.facility_id == f.facility_id,
            models.AttendanceRecord.attendance_date >= start_date,
            models.AttendanceRecord.status.in_(["present", "late"])
        ).count()
        
        attendance_rate = (total_present / total_scheduled * 100.0) if total_scheduled > 0 else 85.0
        
        # 3. Bed Turnover Efficiency (20% weight)
        bed_records = db.query(models.BedStatus).filter(
            models.BedStatus.facility_id == f.facility_id
        ).all()
        if bed_records:
            occ_list = [r.occupied_beds / r.total_beds * 100 for r in bed_records if r.total_beds > 0]
            if occ_list:
                avg_occ = np.mean(occ_list)
                # Ideal occupancy is between 50% and 80%
                if 50.0 <= avg_occ <= 80.0:
                    beds_score = 95.0
                else:
                    beds_score = max(30.0, 100.0 - abs(65.0 - avg_occ))
            else:
                beds_score = 75.0
        else:
            beds_score = 75.0
            
        # 4. Test Availability (15% weight)
        tests_count = db.query(models.DiagnosticTest).filter(models.DiagnosticTest.is_mandated == True).count()
        audits_subquery = db.query(
            models.DiagnosticAudit.test_id,
            func.max(models.DiagnosticAudit.audit_date).label("max_date")
        ).filter(models.DiagnosticAudit.facility_id == f.facility_id).group_by(models.DiagnosticAudit.test_id).subquery()
        
        latest_audits = db.query(models.DiagnosticAudit).join(
            audits_subquery,
            (models.DiagnosticAudit.test_id == audits_subquery.c.test_id) &
            (models.DiagnosticAudit.audit_date == audits_subquery.c.max_date)
        ).filter(models.DiagnosticAudit.facility_id == f.facility_id).all()
        
        available_tests = sum(1 for x in latest_audits if x.status in ["available", "limited"])
        tests_score = (available_tests / tests_count * 100) if tests_count > 0 else 80.0
        
        # 5. Data Completeness (10% weight)
        # Log counts in last 30 days
        footfall_days = db.query(models.FootfallRecord.record_date).filter(
            models.FootfallRecord.facility_id == f.facility_id,
            models.FootfallRecord.record_date >= start_date
        ).distinct().count()
        
        completeness_score = (footfall_days / 30.0 * 100.0)
        completeness_score = max(20.0, min(100.0, completeness_score))
        
        # 6. Composite Score
        composite = (
            0.30 * stock_score +
            0.25 * attendance_rate +
            0.20 * beds_score +
            0.15 * tests_score +
            0.10 * completeness_score
        )
        
        # Flagging Rules
        is_flagged = False
        reasons = []
        
        if composite < 60.0:
            is_flagged = True
            reasons.append(f"Composite health score is critical ({round(composite, 1)}).")
            
        # Single-metric override
        if stock_score < 40.0:
            is_flagged = True
            reasons.append("Critical Stock Outages: inventory reliability is under 40%.")
        if attendance_rate < 50.0:
            is_flagged = True
            reasons.append("Severe staffing absences: attendance is under 50%.")
        if tests_score < 50.0:
            is_flagged = True
            reasons.append("FDSI compliance gap: Mandated diagnostic test availability is under 50%.")
            
        # Save score
        # Check if record for this month already exists
        existing = db.query(models.FacilityScore).filter(
            models.FacilityScore.facility_id == f.facility_id,
            models.FacilityScore.period_end == today
        ).first()
        
        if existing:
            existing.stock_reliability = round(stock_score, 1)
            existing.attendance_rate = round(attendance_rate, 1)
            existing.bed_turnover = round(beds_score, 1)
            existing.test_availability = round(tests_score, 1)
            existing.composite_score = round(composite, 1)
            existing.is_flagged = is_flagged
            existing.flag_reasons = reasons
        else:
            score_rec = models.FacilityScore(
                facility_id=f.facility_id,
                period_start=start_date,
                period_end=today,
                stock_reliability=round(stock_score, 1),
                attendance_rate=round(attendance_rate, 1),
                bed_turnover=round(beds_score, 1),
                test_availability=round(tests_score, 1),
                composite_score=round(composite, 1),
                is_flagged=is_flagged,
                flag_reasons=reasons
            )
            db.add(score_rec)
            
        scores_updated += 1
        
    db.commit()
    return scores_updated

@router.post("/compute")
def trigger_compute_scores(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    count = compute_scores_for_all(db)
    return {"status": "success", "message": f"Recalculated rolling composite scores for {count} facilities."}

@router.get("/facility/{facility_id}")
def get_facility_score(
    facility_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    score = db.query(models.FacilityScore).filter(
        models.FacilityScore.facility_id == facility_id
    ).order_by(models.FacilityScore.computed_at.desc()).first()
    
    if not score:
        # Trigger dynamic compute if empty
        compute_scores_for_all(db)
        score = db.query(models.FacilityScore).filter(
            models.FacilityScore.facility_id == facility_id
        ).order_by(models.FacilityScore.computed_at.desc()).first()
        
    if not score:
        raise HTTPException(status_code=404, detail="Scores details not found")
        
    fac = db.query(models.Facility).filter(models.Facility.facility_id == facility_id).first()
    
    # Generate Natural Language Explainer
    explainer = []
    if score.composite_score >= 75:
        explainer.append(f"{fac.name} is in good operational status. Resources and staffing check-ins are fully aligned.")
    else:
        explainer.append(f"{fac.name} requires oversight attention due to the following sub-metric issues:")
        if score.stock_reliability < 70:
            explainer.append(f"- Inventory stock reliability is low ({score.stock_reliability}%). Multiple essential items have crossed threshold requirements.")
        if score.attendance_rate < 75:
            explainer.append(f"- Staff roster attendance rates are low ({score.attendance_rate}%). Lateness and coverage gaps are outstanding.")
        if score.test_availability < 70:
            explainer.append(f"- Diagnostic compliance is low ({score.test_availability}%). Key mandated reagent kits are missing.")
            
    return {
        "score_id": score.score_id,
        "facility_id": score.facility_id,
        "facility_name": fac.name,
        "composite_score": float(score.composite_score),
        "stock_reliability": float(score.stock_reliability),
        "attendance_rate": float(score.attendance_rate),
        "bed_turnover": float(score.bed_turnover),
        "test_availability": float(score.test_availability),
        "is_flagged": score.is_flagged,
        "flag_reasons": score.flag_reasons,
        "explainer": " ".join(explainer),
        "computed_at": score.computed_at.isoformat()
    }

@router.get("/district")
def get_district_scores_ranking(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Auto compute if empty
    existing_count = db.query(models.FacilityScore).count()
    if existing_count == 0:
        compute_scores_for_all(db)
        
    # Get latest scores per facility
    subquery = db.query(
        models.FacilityScore.facility_id,
        func.max(models.FacilityScore.computed_at).label("max_ts")
    ).group_by(models.FacilityScore.facility_id).subquery()
    
    results = db.query(models.FacilityScore).join(
        subquery,
        (models.FacilityScore.facility_id == subquery.c.facility_id) &
        (models.FacilityScore.computed_at == subquery.c.max_ts)
    ).all()
    
    ranked_list = []
    for r in results:
        fac = db.query(models.Facility).filter(models.Facility.facility_id == r.facility_id).first()
        ranked_list.append({
            "facility_id": r.facility_id,
            "facility_name": fac.name if fac else "Facility",
            "block": fac.block if fac else "Block",
            "type": fac.type if fac else "PHC",
            "composite_score": float(r.composite_score),
            "stock_reliability": float(r.stock_reliability),
            "attendance_rate": float(r.attendance_rate),
            "bed_turnover": float(r.bed_turnover),
            "test_availability": float(r.test_availability),
            "is_flagged": r.is_flagged,
            "flag_reasons": r.flag_reasons
        })
        
    # Sort descending by composite score
    ranked_list.sort(key=lambda x: x["composite_score"], reverse=True)
    return ranked_list

@router.get("/flagged")
def get_flagged_facilities(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    scores = get_district_scores_ranking(db, current_user)
    return [x for x in scores if x["is_flagged"]]
