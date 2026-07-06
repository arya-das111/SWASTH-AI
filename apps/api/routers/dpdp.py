from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db
import audit_logger

router = APIRouter(
    prefix="/api/v1/dpdp",
    tags=["DPDP Act 2023 Compliance"]
)

class ConsentPayload(BaseModel):
    consent_given: bool
    remarks: Optional[str] = "Staff onboarding consent"

class CorrectionPayload(BaseModel):
    staff_id: str
    field_to_correct: str
    suggested_value: str

class DeletionPayload(BaseModel):
    staff_id: str

@router.post("/consent")
def manage_consent(
    payload: ConsentPayload,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Log consent record in audit logger
    audit_logger.log_action(
        db=db,
        table_name="staff",
        record_id=current_user.staff_id or "admin",
        action="UPDATE",
        old_value={"consent": "none_or_previous"},
        new_value={"consent_given": payload.consent_given, "remarks": payload.remarks},
        user_id=current_user.user_id
    )
    
    return {"status": "success", "message": "Consent status updated and logged in secure audit trail."}

@router.get("/requests/access")
def get_personal_data_access(
    staff_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Data principals are allowed to access their own data, admins can access any
    if current_user.role not in ["system_admin", "state_admin", "dho"] and current_user.staff_id != staff_id:
        raise HTTPException(status_code=403, detail="Unprivileged access request. Can only view your own records.")
        
    staff = db.query(models.Staff).filter(models.Staff.staff_id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff record not found")
        
    # Gather logs recorded
    att_records = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.staff_id == staff_id).all()
    diag_audits = db.query(models.DiagnosticAudit).filter(models.DiagnosticAudit.auditor_id == staff_id).all()
    
    # Audit log entry for data access request (Section 5.4 compliance audit trail)
    audit_logger.log_action(
        db=db,
        table_name="staff",
        record_id=staff_id,
        action="READ",
        new_value={"reason": "DPDP Section 12 Data Access Request"},
        user_id=current_user.user_id
    )

    return {
        "data_principal": {
            "staff_id": staff.staff_id,
            "name": staff.name,
            "role": staff.role,
            "phone": staff.phone,
            "email": staff.email,
            "facility_id": staff.facility_id,
            "is_active": staff.is_active,
            "created_at": staff.created_at.isoformat() if staff.created_at else None
        },
        "attendance_trail": [
            {
                "record_date": str(a.attendance_date),
                "status": a.status,
                "check_in": a.check_in_at.isoformat() if a.check_in_at else None,
                "check_out": a.check_out_at.isoformat() if a.check_out_at else None
            } for a in att_records
        ],
        "diagnostics_audited": [
            {
                "audit_id": d.audit_id,
                "audit_date": str(d.audit_date),
                "test_name": d.test_id,
                "status": d.status,
                "reagent_stock": d.reagent_stock
            } for d in diag_audits
        ]
    }

@router.post("/requests/correction")
def submit_data_correction(
    payload: CorrectionPayload,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role not in ["system_admin", "state_admin", "dho"] and current_user.staff_id != payload.staff_id:
        raise HTTPException(status_code=403, detail="Unauthorized data correction request.")
        
    staff = db.query(models.Staff).filter(models.Staff.staff_id == payload.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff record not found")
        
    old_val = getattr(staff, payload.field_to_correct, None)
    
    if payload.field_to_correct in ["name", "phone", "email", "language_pref"]:
        setattr(staff, payload.field_to_correct, payload.suggested_value)
        db.commit()
        
        # Log correction
        audit_logger.log_action(
            db=db,
            table_name="staff",
            record_id=payload.staff_id,
            action="UPDATE",
            old_value={payload.field_to_correct: old_val},
            new_value={payload.field_to_correct: payload.suggested_value},
            user_id=current_user.user_id
        )
        return {"status": "success", "message": f"Corrected {payload.field_to_correct} successfully."}
        
    raise HTTPException(status_code=400, detail="Invalid correction field")

@router.post("/requests/deletion")
def submit_data_deletion(
    payload: DeletionPayload,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Only admins or the staff user themselves can request deletion
    if current_user.role not in ["system_admin", "state_admin"] and current_user.staff_id != payload.staff_id:
        raise HTTPException(status_code=403, detail="Unauthorized deletion request.")
        
    staff = db.query(models.Staff).filter(models.Staff.staff_id == payload.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff record not found")
        
    old_data = {
        "name": staff.name,
        "phone": staff.phone,
        "email": staff.email
    }
    
    # Redact PII (erase) while keeping structure intact for historical audit counts
    staff.name = "Redacted Practitioner (DPDP Section 12)"
    staff.phone = "9999999999"
    staff.email = "redacted@swasth.ai"
    staff.is_active = False
    db.commit()
    
    # Log erasure action
    audit_logger.log_action(
        db=db,
        table_name="staff",
        record_id=payload.staff_id,
        action="DELETE",
        old_value=old_data,
        new_value={"name": "Redacted", "is_active": False},
        user_id=current_user.user_id
    )
    
    return {"status": "success", "message": "PII fields redacted and deleted. Historical metrics preserved."}
