from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard Operations"]
)

@router.get("/facility/{facility_id}")
def get_facility_dashboard(
    facility_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Enforce facility scoping if not admin/dho
    if current_user.role not in ["dho", "state_admin", "system_admin"] and current_user.facility_id != facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to view this facility's dashboard"
        )
        
    facility = db.query(models.Facility).filter(models.Facility.facility_id == facility_id).first()
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
        
    today = date.today()
    
    # 1. Stock Aggregates
    stock_query = db.query(models.StockItem).filter(models.StockItem.facility_id == facility_id).all()
    total_skus = len(stock_query)
    below_t = sum(1 for x in stock_query if x.quantity < x.min_threshold and x.quantity > 0)
    stockouts = sum(1 for x in stock_query if x.quantity == 0)
    target_date = today + timedelta(days=30)
    expiring = sum(1 for x in stock_query if x.expiry_date and x.expiry_date <= target_date and x.expiry_date >= today)
    
    # 2. Bed Occupancy
    # Get latest snapshots
    subquery = db.query(
        models.BedStatus.ward_type,
        func.max(models.BedStatus.timestamp).label("max_ts")
    ).filter(models.BedStatus.facility_id == facility_id).group_by(models.BedStatus.ward_type).subquery()
    
    bed_statuses = db.query(models.BedStatus).join(
        subquery,
        (models.BedStatus.ward_type == subquery.c.ward_type) & 
        (models.BedStatus.timestamp == subquery.c.max_ts)
    ).filter(models.BedStatus.facility_id == facility_id).all()
    
    total_beds = sum(w.total_beds for w in bed_statuses)
    occupied_beds = sum(w.occupied_beds for w in bed_statuses)
    bed_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0.0
    
    # 3. Attendance Status
    attendance_records = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.facility_id == facility_id,
        models.AttendanceRecord.attendance_date == today
    ).all()
    
    total_scheduled = len(attendance_records)
    total_present = sum(1 for x in attendance_records if x.status in ["present", "late"])
    attendance_rate = (total_present / total_scheduled * 100) if total_scheduled > 0 else 100.0
    
    # 4. Diagnostics Availability
    tests_count = db.query(models.DiagnosticTest).filter(models.DiagnosticTest.is_mandated == True).count()
    
    # Query latest audit for facility
    audits_subquery = db.query(
        models.DiagnosticAudit.test_id,
        func.max(models.DiagnosticAudit.audit_date).label("max_date")
    ).filter(models.DiagnosticAudit.facility_id == facility_id).group_by(models.DiagnosticAudit.test_id).subquery()
    
    latest_audits = db.query(models.DiagnosticAudit).join(
        audits_subquery,
        (models.DiagnosticAudit.test_id == audits_subquery.c.test_id) &
        (models.DiagnosticAudit.audit_date == audits_subquery.c.max_date)
    ).filter(models.DiagnosticAudit.facility_id == facility_id).all()
    
    available_tests = sum(1 for x in latest_audits if x.status in ["available", "limited"])
    compliance_rate = (available_tests / tests_count * 100) if tests_count > 0 else 100.0
    
    # 5. Footfall Today
    footfall_records = db.query(models.FootfallRecord).filter(
        models.FootfallRecord.facility_id == facility_id,
        models.FootfallRecord.record_date == today
    ).all()
    opd_today = sum(x.opd_count for x in footfall_records)
    ipd_today = sum(x.ipd_count for x in footfall_records)
    
    # 6. Composite Score
    score_record = db.query(models.FacilityScore).filter(
        models.FacilityScore.facility_id == facility_id
    ).order_by(models.FacilityScore.computed_at.desc()).first()
    
    comp_score = float(score_record.composite_score) if score_record else 85.0
    is_flagged = score_record.is_flagged if score_record else False
    flag_reasons = score_record.flag_reasons if score_record else []
    
    return {
        "facility_id": facility_id,
        "facility_name": facility.name,
        "type": facility.type,
        "district": facility.district,
        "block": facility.block,
        "composite_score": comp_score,
        "is_flagged": is_flagged,
        "flag_reasons": flag_reasons,
        "stock": {
            "total_skus": total_skus,
            "below_threshold": below_t,
            "stockouts": stockouts,
            "expiring_soon": expiring
        },
        "beds": {
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "occupancy_rate": round(bed_rate, 1)
        },
        "attendance": {
            "scheduled": total_scheduled,
            "present": total_present,
            "attendance_rate": round(attendance_rate, 1)
        },
        "diagnostics": {
            "mandated_total": tests_count,
            "available_total": available_tests,
            "compliance_rate": round(compliance_rate, 1)
        },
        "footfall": {
            "opd": opd_today,
            "ipd": ipd_today
        }
    }

@router.get("/district")
def get_district_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    today = date.today()
    district = "Lucknow"
    
    # 1. Total & Flagged facilities
    facilities = db.query(models.Facility).filter(models.Facility.district == district).all()
    total_facs = len(facilities)
    fac_ids = [f.facility_id for f in facilities]
    
    # Flagged count
    flagged_count = db.query(models.FacilityScore).filter(
        models.FacilityScore.facility_id.in_(fac_ids),
        models.FacilityScore.is_flagged == True
    ).count()
    
    # 2. Stock Alerts Count
    stock_alerts = db.query(models.Alert).filter(
        models.Alert.facility_id.in_(fac_ids),
        models.Alert.alert_type.in_(["stock_out", "stock_low"]),
        models.Alert.status == "active"
    ).count()
    
    # 3. Footfall Today
    footfall_today = db.query(func.sum(models.FootfallRecord.opd_count)).filter(
        models.FootfallRecord.facility_id.in_(fac_ids),
        models.FootfallRecord.record_date == today
    ).scalar() or 0
    
    # 4. Beds Status
    subquery = db.query(
        models.BedStatus.facility_id,
        models.BedStatus.ward_type,
        func.max(models.BedStatus.timestamp).label("max_ts")
    ).filter(models.BedStatus.facility_id.in_(fac_ids)).group_by(models.BedStatus.facility_id, models.BedStatus.ward_type).subquery()
    
    bed_records = db.query(models.BedStatus).join(
        subquery,
        (models.BedStatus.facility_id == subquery.c.facility_id) &
        (models.BedStatus.ward_type == subquery.c.ward_type) &
        (models.BedStatus.timestamp == subquery.c.max_ts)
    ).all()
    
    total_beds = sum(r.total_beds for r in bed_records)
    occupied_beds = sum(r.occupied_beds for r in bed_records)
    avg_bed_occ = (occupied_beds / total_beds * 100) if total_beds > 0 else 0.0
    
    # 5. Attendance Status
    present_staff = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.facility_id.in_(fac_ids),
        models.AttendanceRecord.attendance_date == today,
        models.AttendanceRecord.status.in_(["present", "late"])
    ).count()
    
    scheduled_staff = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.facility_id.in_(fac_ids),
        models.AttendanceRecord.attendance_date == today
    ).count()
    avg_attendance_rate = (present_staff / scheduled_staff * 100) if scheduled_staff > 0 else 100.0
    
    # 6. Alerts
    active_alerts = db.query(models.Alert).filter(
        models.Alert.facility_id.in_(fac_ids),
        models.Alert.status == "active"
    ).all()
    critical_alerts = sum(1 for x in active_alerts if x.severity == "critical")
    warning_alerts = sum(1 for x in active_alerts if x.severity in ["high", "medium"])
    
    return {
        "district": district,
        "total_facilities": total_facs,
        "flagged_facilities": flagged_count,
        "footfall_today": footfall_today,
        "stock": {
            "active_alerts": stock_alerts
        },
        "beds": {
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "occupancy_rate": round(avg_bed_occ, 1)
        },
        "attendance": {
            "present_today": present_staff,
            "scheduled_today": scheduled_staff,
            "attendance_rate": round(avg_attendance_rate, 1)
        },
        "alerts": {
            "total": len(active_alerts),
            "critical": critical_alerts,
            "warning": warning_alerts
        }
    }

@router.get("/state")
def get_state_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["state_admin", "system_admin"]))
):
    # State Dashboard: Return rankings of districts
    # We will simulate 4 districts: Lucknow, Kanpur, Varanasi, Agra
    # We aggregate Lucknow dynamically from DB, others are mocked/simulated
    lucknow_data = get_district_dashboard(db, current_user)
    
    districts = [
        {
            "district": "Lucknow",
            "health_score": 88.5,
            "active_facilities": lucknow_data["total_facilities"],
            "flagged_facilities": lucknow_data["flagged_facilities"],
            "avg_bed_occupancy": lucknow_data["beds"]["occupancy_rate"],
            "active_alerts": lucknow_data["alerts"]["total"],
            "attendance_rate": lucknow_data["attendance"]["attendance_rate"]
        },
        {
            "district": "Kanpur Nagar",
            "health_score": 82.1,
            "active_facilities": 32,
            "flagged_facilities": 4,
            "avg_bed_occupancy": 64.2,
            "active_alerts": 12,
            "attendance_rate": 86.5
        },
        {
            "district": "Varanasi",
            "health_score": 91.0,
            "active_facilities": 18,
            "flagged_facilities": 1,
            "avg_bed_occupancy": 72.8,
            "active_alerts": 2,
            "attendance_rate": 93.4
        },
        {
            "district": "Agra",
            "health_score": 79.4,
            "active_facilities": 22,
            "flagged_facilities": 6,
            "avg_bed_occupancy": 52.1,
            "active_alerts": 18,
            "attendance_rate": 78.9
        }
    ]
    
    # Sort by health score descending
    districts.sort(key=lambda x: x["health_score"], reverse=True)
    
    return {
        "state": "Uttar Pradesh",
        "total_districts": len(districts),
        "total_facilities": sum(d["active_facilities"] for d in districts),
        "flagged_facilities": sum(d["flagged_facilities"] for d in districts),
        "active_alerts": sum(d["active_alerts"] for d in districts),
        "districts": districts
    }
