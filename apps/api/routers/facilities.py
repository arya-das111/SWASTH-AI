from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/facilities",
    tags=["Facilities"]
)

# Admin role checker for write operations
admin_checker = auth.RoleChecker(["system_admin"])

@router.post("", status_code=status.HTTP_201_CREATED)
def onboard_facility(
    facility_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_checker)
):
    # Validate required fields
    required = ["name", "type", "district", "state"]
    for field in required:
        if field not in facility_data or not facility_data[field]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' is required"
            )
            
    # HFR check
    hfr_id = facility_data.get("hfr_id")
    if hfr_id:
        existing = db.query(models.Facility).filter(models.Facility.hfr_id == hfr_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Facility with HFR ID '{hfr_id}' already onboarded"
            )
            
    facility = models.Facility(
        hfr_id=hfr_id,
        name=facility_data["name"],
        type=facility_data["type"],
        district=facility_data["district"],
        block=facility_data.get("block"),
        state=facility_data["state"],
        latitude=facility_data.get("latitude"),
        longitude=facility_data.get("longitude"),
        total_bed_capacity=facility_data.get("total_bed_capacity", 0),
        default_language=facility_data.get("default_language", "en")
    )
    db.add(facility)
    db.commit()
    db.refresh(facility)
    return facility

@router.get("")
def list_facilities(
    district: Optional[str] = None,
    block: Optional[str] = None,
    facility_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.Facility).filter(models.Facility.is_active == True)
    
    if district:
        query = query.filter(models.Facility.district == district)
    if block:
        query = query.filter(models.Facility.block == block)
    if facility_type:
        query = query.filter(models.Facility.type == facility_type)
        
    return query.all()

@router.get("/{facility_id}")
def get_facility(
    facility_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    facility = db.query(models.Facility).filter(
        models.Facility.facility_id == facility_id,
        models.Facility.is_active == True
    ).first()
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
    return facility

@router.get("/{facility_id}/staff")
def list_facility_staff(
    facility_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify facility exists
    facility = db.query(models.Facility).filter(models.Facility.facility_id == facility_id).first()
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
        
    staff = db.query(models.Staff).filter(
        models.Staff.facility_id == facility_id,
        models.Staff.is_active == True
    ).all()
    return staff

@router.post("/{facility_id}/staff", status_code=status.HTTP_201_CREATED)
def add_facility_staff(
    facility_id: str,
    staff_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_checker)
):
    # Verify facility exists
    facility = db.query(models.Facility).filter(models.Facility.facility_id == facility_id).first()
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility not found"
        )
        
    required = ["name", "role"]
    for field in required:
        if field not in staff_data or not staff_data[field]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' is required for staff onboarding"
            )
            
    staff = models.Staff(
        facility_id=facility_id,
        name=staff_data["name"],
        role=staff_data["role"],
        phone=staff_data.get("phone"),
        email=staff_data.get("email"),
        language_pref=staff_data.get("language_pref", "en")
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff
