from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta, datetime
import pandas as pd
import numpy as np
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/anomalies",
    tags=["Early-Warning Anomalies"]
)

# Real-time scan and populate anomalies
def run_anomaly_scanner(db: Session, district: str = "Lucknow"):
    today = date.today()
    facilities = db.query(models.Facility).filter(models.Facility.district == district).all()
    
    anomalies_created = 0
    
    for f in facilities:
        # 1. OPD Footfall Surge Check (>2 SD above rolling 30-day mean)
        start_date = datetime.now() - timedelta(days=30)
        footfall_history = db.query(models.FootfallRecord).filter(
            models.FootfallRecord.facility_id == f.facility_id,
            models.FootfallRecord.record_date >= start_date.date()
        ).all()
        
        if len(footfall_history) >= 5:
            counts = [r.opd_count + r.ipd_count for r in footfall_history]
            mean_val = np.mean(counts)
            std_val = np.std(counts)
            
            # Today's record
            today_rec = next((x for x in footfall_history if x.record_date == today), None)
            if today_rec:
                today_val = today_rec.opd_count + today_rec.ipd_count
                if std_val > 0 and today_val > (mean_val + 2.0 * std_val):
                    # Check if alert already exists
                    title = f"Surge: OPD Footfall Anomaly at {f.name}"
                    existing = db.query(models.Alert).filter(
                        models.Alert.facility_id == f.facility_id,
                        models.Alert.title == title,
                        models.Alert.status == "active"
                    ).first()
                    if not existing:
                        alert = models.Alert(
                            facility_id=f.facility_id,
                            alert_type="anomaly",
                            severity="high",
                            title=title,
                            message=f"Today's total patients count ({today_val}) is over 2.0 SD above the 30-day average ({round(mean_val, 1)}). Possible epidemic spike or data log anomaly.",
                            status="active",
                            extra_metadata={"category": "footfall", "today_value": today_val, "mean": round(mean_val, 1), "std": round(std_val, 1)}
                        )
                        db.add(alert)
                        anomalies_created += 1

        # 2. Staff Attendance Anomaly (>50% scheduled staff absent today)
        attendance_today = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.facility_id == f.facility_id,
            models.AttendanceRecord.attendance_date == today
        ).all()
        
        if len(attendance_today) >= 3:
            total_roster = len(attendance_today)
            absent_count = sum(1 for x in attendance_today if x.status == "absent")
            absence_rate = (absent_count / total_roster * 100) if total_roster > 0 else 0.0
            
            if absence_rate >= 50.0:
                title = f"Alert: Mass Staff Absence at {f.name}"
                existing = db.query(models.Alert).filter(
                    models.Alert.facility_id == f.facility_id,
                    models.Alert.title == title,
                    models.Alert.status == "active"
                ).first()
                if not existing:
                    alert = models.Alert(
                        facility_id=f.facility_id,
                        alert_type="anomaly",
                        severity="critical",
                        title=title,
                        message=f"{absent_count} out of {total_roster} rostered staff are marked ABSENT today ({round(absence_rate, 1)}%). Operation integrity compromised.",
                        status="active",
                        extra_metadata={"category": "attendance", "absent_count": absent_count, "total_roster": total_roster}
                    )
                    db.add(alert)
                    anomalies_created += 1

        # 3. Bed Occupancy jump (>30% change in 24 hours)
        # Fetch latest two status reports
        bed_history = db.query(models.BedStatus).filter(
            models.BedStatus.facility_id == f.facility_id
        ).order_by(models.BedStatus.timestamp.desc()).limit(2).all()
        
        if len(bed_history) == 2:
            latest = bed_history[0]
            prev = bed_history[1]
            if latest.total_beds > 0:
                diff_pct = abs((latest.occupied_beds - prev.occupied_beds) / latest.total_beds * 100)
                if diff_pct >= 30.0:
                    title = f"Spike: Bed Occupancy Jump at {f.name}"
                    existing = db.query(models.Alert).filter(
                        models.Alert.facility_id == f.facility_id,
                        models.Alert.title == title,
                        models.Alert.status == "active"
                    ).first()
                    if not existing:
                        alert = models.Alert(
                            facility_id=f.facility_id,
                            alert_type="anomaly",
                            severity="medium",
                            title=title,
                            message=f"Occupancy in General ward shifted from {prev.occupied_beds} to {latest.occupied_beds} within 24h (a {round(diff_pct, 1)}% shift in total beds). Inspect immediate admissions load.",
                            status="active",
                            extra_metadata={"category": "beds", "latest": latest.occupied_beds, "prev": prev.occupied_beds}
                        )
                        db.add(alert)
                        anomalies_created += 1

    if anomalies_created > 0:
        db.commit()

@router.get("")
def list_anomalies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Scan real-time streams
    run_anomaly_scanner(db)
    
    # Query anomaly alerts
    query = db.query(models.Alert).filter(models.Alert.alert_type == "anomaly")
    
    # Restrict to user's facility if DHO is not requesting
    if current_user.role not in ["dho", "state_admin", "system_admin"]:
        query = query.filter(models.Alert.facility_id == current_user.facility_id)
        
    results = query.order_by(models.Alert.generated_at.desc()).all()
    
    anomalies_list = []
    for r in results:
        fac_name = "District-wide"
        if r.facility_id:
            fac = db.query(models.Facility).filter(models.Facility.facility_id == r.facility_id).first()
            if fac:
                fac_name = fac.name
                
        anomalies_list.append({
            "alert_id": r.alert_id,
            "facility_id": r.facility_id,
            "facility_name": fac_name,
            "severity": r.severity,
            "title": r.title,
            "message": r.message,
            "status": r.status,
            "extra_metadata": r.extra_metadata,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None
        })
        
    return anomalies_list

@router.post("/{alert_id}/classify")
def classify_anomaly(
    alert_id: str,
    classification: str,  # 'true_positive' or 'false_positive'
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    alert = db.query(models.Alert).filter(
        models.Alert.alert_id == alert_id,
        models.Alert.alert_type == "anomaly"
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Anomaly alert not found")
        
    if classification not in ["true_positive", "false_positive"]:
        raise HTTPException(status_code=400, detail="Invalid classification. Must be true_positive or false_positive")
        
    meta = alert.extra_metadata or {}
    meta["classification"] = classification
    alert.extra_metadata = meta
    alert.status = "dismissed" if classification == "false_positive" else "resolved"
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    return {"status": "success", "message": f"Anomaly marked as {classification} and resolved."}

@router.get("/stats")
def get_anomalies_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    # Scan real-time streams
    run_anomaly_scanner(db)
    
    anomalies = db.query(models.Alert).filter(models.Alert.alert_type == "anomaly").all()
    
    total = len(anomalies)
    active = sum(1 for x in anomalies if x.status == "active")
    true_p = 0
    false_p = 0
    
    for a in anomalies:
        meta = a.extra_metadata or {}
        if meta.get("classification") == "true_positive":
            true_p += 1
        elif meta.get("classification") == "false_positive":
            false_p += 1
            
    # Classifications rate
    classified = true_p + false_p
    true_positive_rate = (true_p / classified * 100) if classified > 0 else 100.0
    
    return {
        "total_detected": total,
        "active_unresolved": active,
        "true_positives": true_p,
        "false_positives": false_p,
        "true_positive_rate_percent": round(true_positive_rate, 1)
    }
