from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/diagnostics",
    tags=["Diagnostics Auditing"]
)

# Admin check
admin_checker = auth.RoleChecker(["system_admin"])

@router.get("/tests")
def list_diagnostic_tests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.DiagnosticTest).all()

@router.post("/tests", status_code=status.HTTP_201_CREATED)
def create_diagnostic_test(
    test_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_checker)
):
    required = ["test_name"]
    for field in required:
        if field not in test_data or not test_data[field]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' is required"
            )
            
    existing = db.query(models.DiagnosticTest).filter(models.DiagnosticTest.test_name == test_data["test_name"]).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test name already exists in catalog"
        )
        
    test = models.DiagnosticTest(
        test_name=test_data["test_name"],
        category=test_data.get("category"),
        is_mandated=test_data.get("is_mandated", False)
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return test

@router.post("/audit", status_code=status.HTTP_201_CREATED)
def submit_diagnostic_audit(
    audit_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    required = ["test_id", "status"]
    for field in required:
        if field not in audit_data or audit_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' is required"
            )
            
    facility_id = audit_data.get("facility_id")
    if current_user.role not in ["dho", "system_admin"]:
        facility_id = current_user.facility_id
        
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility ID is required"
        )
        
    t_id = audit_data["test_id"]
    status_str = audit_data["status"]
    
    # Verify test exists
    test = db.query(models.DiagnosticTest).filter(models.DiagnosticTest.test_id == t_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test SKU not found in catalog"
        )
        
    # Check trigger rules for FDSI gaps
    if test.is_mandated and status_str == "unavailable":
        alert = models.Alert(
            facility_id=facility_id,
            alert_type="test_unavailable",
            severity="high",
            title=f"FDSI Compliance Gap: {test.test_name} Unavailable",
            message=f"Mandated Free Diagnostic test '{test.test_name}' is currently unavailable at this facility.",
            status="active",
            routed_to_role="medical_officer",
            extra_metadata={"test_id": t_id, "test_name": test.test_name}
        )
        db.add(alert)
        
    audit = models.DiagnosticAudit(
        facility_id=facility_id,
        test_id=t_id,
        status=status_str,
        reagent_stock=audit_data.get("reagent_stock", 0),
        audit_date=date.today(),
        auditor_id=current_user.staff_id or current_user.user_id,
        notes=audit_data.get("notes"),
        attachment_url=audit_data.get("attachment_url")
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit

@router.get("/mandated-gaps")
def list_mandated_test_gaps(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    # Free Diagnostics Service Initiative (FDSI) compliance audit
    facilities = db.query(models.Facility).filter(models.Facility.district == "Lucknow").all()
    mandated_tests = db.query(models.DiagnosticTest).filter(models.DiagnosticTest.is_mandated == True).all()
    
    gaps = []
    for f in facilities:
        facility_gaps = []
        for t in mandated_tests:
            # Query latest audit for this test
            latest_audit = db.query(models.DiagnosticAudit).filter(
                models.DiagnosticAudit.facility_id == f.facility_id,
                models.DiagnosticAudit.test_id == t.test_id
            ).order_by(models.DiagnosticAudit.audit_date.desc()).first()
            
            # If never audited or marked unavailable, it's a gap
            if not latest_audit or latest_audit.status == "unavailable":
                facility_gaps.append({
                    "test_id": t.test_id,
                    "test_name": t.test_name,
                    "category": t.category,
                    "last_audit_date": latest_audit.audit_date.isoformat() if latest_audit else None
                })
                
        if facility_gaps:
            gaps.append({
                "facility_id": f.facility_id,
                "facility_name": f.name,
                "type": f.type,
                "block": f.block,
                "missing_mandated_tests": facility_gaps,
                "compliance_score": round((len(mandated_tests) - len(facility_gaps)) / len(mandated_tests) * 100, 1)
            })
            
    return gaps
