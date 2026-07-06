from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta, datetime
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/footfall",
    tags=["Patient Footfall"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def log_footfall(
    footfall_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    required = ["opd_count", "ipd_count"]
    for field in required:
        if field not in footfall_data or footfall_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' is required"
            )
            
    # Enforce facility scopes for facility staff
    facility_id = footfall_data.get("facility_id")
    if current_user.role not in ["dho", "system_admin"]:
        facility_id = current_user.facility_id
        
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility ID is required"
        )
        
    dept = footfall_data.get("department", "General")
    rec_date = footfall_data.get("record_date")
    if rec_date:
        record_date = date.fromisoformat(rec_date)
    else:
        record_date = date.today()
        
    opd_count = footfall_data["opd_count"]
    ipd_count = footfall_data["ipd_count"]
    
    # Check for duplicate record_date + department + facility -> Upsert
    existing = db.query(models.FootfallRecord).filter(
        models.FootfallRecord.facility_id == facility_id,
        models.FootfallRecord.department == dept,
        models.FootfallRecord.record_date == record_date
    ).first()
    
    # Anomaly detection logic: check against 30-day average
    thirty_days_ago = record_date - timedelta(days=30)
    recent = db.query(models.FootfallRecord).filter(
        models.FootfallRecord.facility_id == facility_id,
        models.FootfallRecord.department == dept,
        models.FootfallRecord.record_date >= thirty_days_ago,
        models.FootfallRecord.record_date < record_date
    ).all()
    
    if len(recent) >= 5:
        opd_counts = [r.opd_count for r in recent]
        mean = sum(opd_counts) / len(opd_counts)
        variance = sum((x - mean) ** 2 for x in opd_counts) / len(opd_counts)
        std_dev = variance ** 0.5
        
        if std_dev > 0 and opd_count > (mean + 2 * std_dev):
            # Write alert
            alert = models.Alert(
                facility_id=facility_id,
                alert_type="footfall_spike",
                severity="high",
                title=f"OPD Footfall Spike - {dept}",
                message=f"Unusual patient spike in '{dept}'. Today: {opd_count} patients, 30-day avg: {mean:.1f} (std dev: {std_dev:.1f}).",
                status="active",
                routed_to_role="medical_officer",
                extra_metadata={"opd_count": opd_count, "avg_30_day": mean, "std_dev": std_dev}
            )
            db.add(alert)
            
    if existing:
        existing.opd_count = opd_count
        existing.ipd_count = ipd_count
        existing.recorded_by = current_user.staff_id or current_user.user_id
        db.commit()
        db.refresh(existing)
        return existing
    else:
        record = models.FootfallRecord(
            facility_id=facility_id,
            department=dept,
            record_date=record_date,
            opd_count=opd_count,
            ipd_count=ipd_count,
            source="manual",
            recorded_by=current_user.staff_id or current_user.user_id
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

@router.get("")
def list_footfall(
    facility_id: Optional[str] = None,
    department: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.FootfallRecord)
    
    # Access control
    if current_user.role not in ["dho", "state_admin", "system_admin"]:
        query = query.filter(models.FootfallRecord.facility_id == current_user.facility_id)
    elif facility_id:
        query = query.filter(models.FootfallRecord.facility_id == facility_id)
        
    if department:
        query = query.filter(models.FootfallRecord.department == department)
        
    if start_date:
        query = query.filter(models.FootfallRecord.record_date >= date.fromisoformat(start_date))
    if end_date:
        query = query.filter(models.FootfallRecord.record_date <= date.fromisoformat(end_date))
        
    return query.order_by(models.FootfallRecord.record_date.desc()).all()

@router.get("/trends")
def get_footfall_trends(
    facility_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    fid = facility_id
    if current_user.role not in ["dho", "state_admin", "system_admin"]:
        fid = current_user.facility_id
        
    # Calculate YoY / WoW metrics
    # We will get counts for current week (last 7 days) and previous week (days 8-14 ago)
    today = date.today()
    last_7_start = today - timedelta(days=7)
    prev_7_start = today - timedelta(days=14)
    
    q_curr = db.query(
        func.sum(models.FootfallRecord.opd_count).label("opd"),
        func.sum(models.FootfallRecord.ipd_count).label("ipd")
    ).filter(models.FootfallRecord.record_date >= last_7_start)
    
    q_prev = db.query(
        func.sum(models.FootfallRecord.opd_count).label("opd"),
        func.sum(models.FootfallRecord.ipd_count).label("ipd")
    ).filter(models.FootfallRecord.record_date >= prev_7_start, models.FootfallRecord.record_date < last_7_start)
    
    if fid:
        q_curr = q_curr.filter(models.FootfallRecord.facility_id == fid)
        q_prev = q_prev.filter(models.FootfallRecord.facility_id == fid)
        
    curr_res = q_curr.first()
    prev_res = q_prev.first()
    
    curr_opd = curr_res.opd or 0
    curr_ipd = curr_res.ipd or 0
    prev_opd = prev_res.opd or 0
    prev_ipd = prev_res.ipd or 0
    
    # Compute growth rate
    opd_growth = ((curr_opd - prev_opd) / prev_opd * 100) if prev_opd > 0 else 0
    ipd_growth = ((curr_ipd - prev_ipd) / prev_ipd * 100) if prev_ipd > 0 else 0
    
    # Query last 30 days of daily aggregates for charts
    q_chart = db.query(
        models.FootfallRecord.record_date,
        func.sum(models.FootfallRecord.opd_count).label("opd"),
        func.sum(models.FootfallRecord.ipd_count).label("ipd")
    ).filter(models.FootfallRecord.record_date >= (today - timedelta(days=30)))
    
    if fid:
        q_chart = q_chart.filter(models.FootfallRecord.facility_id == fid)
        
    chart_data = q_chart.group_by(models.FootfallRecord.record_date).order_by(models.FootfallRecord.record_date.asc()).all()
    
    return {
        "current_week": {"opd": curr_opd, "ipd": curr_ipd},
        "previous_week": {"opd": prev_opd, "ipd": prev_ipd},
        "growth": {
            "opd_percentage": round(opd_growth, 1),
            "ipd_percentage": round(ipd_growth, 1)
        },
        "history": [
            {"date": r.record_date.isoformat(), "opd": r.opd, "ipd": r.ipd} for r in chart_data
        ]
    }
