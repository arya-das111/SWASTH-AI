from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import math
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/beds",
    tags=["Beds Management"]
)

# Helper: Haversine distance
def calculate_distance(lat1, lon1, lat2, lon2):
    if not all([lat1, lon1, lat2, lon2]):
        return 9999.0  # Safe fallback if coords missing
    try:
        R = 6371.0 # Earth radius in km
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = math.sin(d_lat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        return round(R * c, 2)
    except Exception:
        return 9999.0

@router.post("/status", status_code=status.HTTP_201_CREATED)
def update_bed_status(
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    required = ["ward_type", "total_beds", "occupied_beds"]
    for field in required:
        if field not in status_data or status_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' is required"
            )
            
    facility_id = status_data.get("facility_id")
    if current_user.role not in ["dho", "system_admin"]:
        facility_id = current_user.facility_id
        
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility ID is required"
        )
        
    ward = status_data["ward_type"]
    total = status_data["total_beds"]
    occupied = status_data["occupied_beds"]
    
    if occupied > total:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Occupied beds ({occupied}) cannot exceed total beds ({total})"
        )
        
    # Check trigger rules for alerts (occupancy > 85%)
    percentage = (occupied / total * 100) if total > 0 else 0
    if percentage > 85.0:
        alert = models.Alert(
            facility_id=facility_id,
            alert_type="bed_capacity",
            severity="high" if percentage < 100 else "critical",
            title=f"High Bed Occupancy - {ward} Ward",
            message=f"Occupancy in '{ward}' ward exceeds safe limits: {occupied}/{total} beds occupied ({percentage:.1f}%).",
            status="active",
            routed_to_role="nurse",
            extra_metadata={"ward_type": ward, "occupied": occupied, "total": total, "occupancy_rate": percentage}
        )
        db.add(alert)
        
    record = models.BedStatus(
        facility_id=facility_id,
        ward_type=ward,
        total_beds=total,
        occupied_beds=occupied,
        updated_by=current_user.staff_id or current_user.user_id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.get("/status")
def get_current_status(
    facility_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    fid = facility_id
    if current_user.role not in ["dho", "state_admin", "system_admin"]:
        fid = current_user.facility_id
        
    if not fid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility ID is required"
        )
        
    # Query latest snapshot per ward
    # SQLite subquery to get latest timestamp per ward
    subquery = db.query(
        models.BedStatus.ward_type,
        func.max(models.BedStatus.timestamp).label("max_ts")
    ).filter(models.BedStatus.facility_id == fid).group_by(models.BedStatus.ward_type).subquery()
    
    records = db.query(models.BedStatus).join(
        subquery,
        (models.BedStatus.ward_type == subquery.c.ward_type) & 
        (models.BedStatus.timestamp == subquery.c.max_ts)
    ).filter(models.BedStatus.facility_id == fid).all()
    
    return records

@router.get("/availability")
def query_district_availability(
    ward_type: str,
    facility_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Find active facilities that have empty beds in requested ward
    # If source facility is provided, compute closest redirections
    src_facility = None
    if facility_id:
        src_facility = db.query(models.Facility).filter(models.Facility.facility_id == facility_id).first()
    elif current_user.facility_id:
        src_facility = db.query(models.Facility).filter(models.Facility.facility_id == current_user.facility_id).first()
        
    # Get latest status for this ward across all facilities in district
    subquery = db.query(
        models.BedStatus.facility_id,
        func.max(models.BedStatus.timestamp).label("max_ts")
    ).filter(models.BedStatus.ward_type == ward_type).group_by(models.BedStatus.facility_id).subquery()
    
    bed_statuses = db.query(models.BedStatus).join(
        subquery,
        (models.BedStatus.facility_id == subquery.c.facility_id) & 
        (models.BedStatus.timestamp == subquery.c.max_ts)
    ).filter(models.BedStatus.ward_type == ward_type).all()
    
    available_options = []
    for bs in bed_statuses:
        empty = bs.total_beds - bs.occupied_beds
        if empty <= 0:
            continue
            
        fac = db.query(models.Facility).filter(models.Facility.facility_id == bs.facility_id).first()
        if not fac or not fac.is_active:
            continue
            
        # Exclude source facility
        if src_facility and fac.facility_id == src_facility.facility_id:
            continue
            
        dist = 0.0
        if src_facility:
            dist = calculate_distance(
                float(src_facility.latitude) if src_facility.latitude else None,
                float(src_facility.longitude) if src_facility.longitude else None,
                float(fac.latitude) if fac.latitude else None,
                float(fac.longitude) if fac.longitude else None
            )
            
        available_options.append({
            "facility_id": fac.facility_id,
            "facility_name": fac.name,
            "type": fac.type,
            "block": fac.block,
            "empty_beds": empty,
            "total_beds": bs.total_beds,
            "distance_km": dist
        })
        
    # Sort by distance
    if src_facility:
        available_options.sort(key=lambda x: x["distance_km"])
    else:
        available_options.sort(key=lambda x: x["empty_beds"], reverse=True)
        
    return available_options[:5] # Top 5 options
