from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone
from pydantic import BaseModel
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/attendance",
    tags=["Staff Attendance"]
)

class CheckInPayload(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@router.post("/checkin", status_code=status.HTTP_201_CREATED)
def checkin_staff(
    payload: Optional[CheckInPayload] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user is not mapped to a staff profile"
        )
        
    today = date.today()
    
    # Check if already checked in today
    existing = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.staff_id == current_user.staff_id,
        models.AttendanceRecord.attendance_date == today
    ).first()
    
    if existing and existing.check_in_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff already checked in today"
        )
        
    now = datetime.now()
    # Late logic: Check-in after 10:00 AM local time
    cutoff = datetime.combine(today, datetime.min.time()).replace(hour=10, minute=0)
    status_str = "late" if now > cutoff else "present"
    
    if existing:
        # Roster was pre-created as absent, we update it
        existing.check_in_at = now
        existing.status = status_str
        existing.source = "app"
        if payload:
            existing.check_in_lat = payload.latitude
            existing.check_in_lon = payload.longitude
        db.commit()
        db.refresh(existing)
        return existing
    else:
        record = models.AttendanceRecord(
            facility_id=current_user.facility_id,
            staff_id=current_user.staff_id,
            role=current_user.role,
            scheduled=True,
            check_in_at=now,
            status=status_str,
            attendance_date=today,
            source="app",
            check_in_lat=payload.latitude if payload else None,
            check_in_lon=payload.longitude if payload else None
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

@router.post("/checkout")
def checkout_staff(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not current_user.staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user is not mapped to a staff profile"
        )
        
    today = date.today()
    record = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.staff_id == current_user.staff_id,
        models.AttendanceRecord.attendance_date == today
    ).first()
    
    if not record or not record.check_in_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No check-in record found for today"
        )
        
    if record.check_out_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff already checked out today"
        )
        
    record.check_out_at = datetime.now()
    db.commit()
    db.refresh(record)
    return record

@router.get("")
def list_attendance(
    facility_id: Optional[str] = None,
    attendance_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.AttendanceRecord)
    
    # Scoping
    if current_user.role not in ["dho", "state_admin", "system_admin"]:
        query = query.filter(models.AttendanceRecord.facility_id == current_user.facility_id)
    elif facility_id:
        query = query.filter(models.AttendanceRecord.facility_id == facility_id)
        
    if attendance_date:
        query = query.filter(models.AttendanceRecord.attendance_date == date.fromisoformat(attendance_date))
    else:
        query = query.filter(models.AttendanceRecord.attendance_date == date.today())
        
    return query.all()

@router.get("/gaps")
def get_coverage_gaps(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    # Coverage Gaps: Find facilities where NO medical_officer is checked in today
    facilities = db.query(models.Facility).filter(models.Facility.district == "Lucknow").all()
    today = date.today()
    
    gaps = []
    for f in facilities:
        mo_present = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.facility_id == f.facility_id,
            models.AttendanceRecord.role == "medical_officer",
            models.AttendanceRecord.attendance_date == today,
            models.AttendanceRecord.status.in_(["present", "late"])
        ).first()
        
        if not mo_present:
            # Check if there is an active alert for this gap
            active_alert = db.query(models.Alert).filter(
                models.Alert.facility_id == f.facility_id,
                models.Alert.alert_type == "attendance_gap",
                models.Alert.status == "active"
            ).first()
            
            if not active_alert:
                alert = models.Alert(
                    facility_id=f.facility_id,
                    alert_type="attendance_gap",
                    severity="critical",
                    title="Absent Doctor Gap Alert",
                    message=f"Medical Officer (MO) is absent or has not checked in today at {f.name}.",
                    status="active",
                    routed_to_role="medical_officer"
                )
                db.add(alert)
                db.commit()
                
            gaps.append({
                "facility_id": f.facility_id,
                "facility_name": f.name,
                "type": f.type,
                "block": f.block
            })
            
    return gaps

@router.get("/patterns")
def get_absenteeism_patterns(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    # Find staff members absent > 3 times in the last 30 days
    last_30 = date.today() - timedelta(days=30)
    
    records = db.query(
        models.AttendanceRecord.staff_id,
        func.count(models.AttendanceRecord.record_id).label("absent_count")
    ).filter(
        models.AttendanceRecord.status == "absent",
        models.AttendanceRecord.attendance_date >= last_30
    ).group_by(models.AttendanceRecord.staff_id).having(func.count(models.AttendanceRecord.record_id) > 3).all()
    
    patterns = []
    for r in records:
        st = db.query(models.Staff).filter(models.Staff.staff_id == r.staff_id).first()
        if not st:
            continue
        fac = db.query(models.Facility).filter(models.Facility.facility_id == st.facility_id).first()
        
        patterns.append({
            "staff_id": st.staff_id,
            "name": st.name,
            "role": st.role,
            "phone": st.phone,
            "facility_name": fac.name if fac else "Unknown",
            "absences_last_30_days": r.absent_count
        })
        
    return patterns
