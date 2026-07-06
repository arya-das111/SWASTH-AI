from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import os
import sys

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/fhir",
    tags=["FHIR R4 Conformance"]
)

@router.get("/Organization/{facility_id}")
def get_fhir_organization(
    facility_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    facility = db.query(models.Facility).filter(models.Facility.facility_id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
        
    return {
        "resourceType": "Organization",
        "id": facility.facility_id,
        "identifier": [
            {
                "system": "https://ndhm.gov.in/hfr",
                "value": facility.hfr_id or "pending-abdm-onboarding"
            }
        ],
        "active": facility.is_active,
        "type": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                        "code": "prov",
                        "display": "Healthcare Provider"
                    }
                ]
            }
        ],
        "name": facility.name,
        "address": [
            {
                "district": facility.district,
                "state": facility.state,
                "country": "India"
            }
        ]
    }

@router.get("/Location/{facility_id}/ward/{ward_type}")
def get_fhir_location(
    facility_id: str,
    ward_type: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bed = db.query(models.BedStatus).filter(
        models.BedStatus.facility_id == facility_id,
        models.BedStatus.ward_type == ward_type
    ).first()
    
    if not bed:
        raise HTTPException(status_code=404, detail="Ward Bed Status record not found")
        
    return {
        "resourceType": "Location",
        "id": bed.status_id,
        "status": "active",
        "name": f"{bed.ward_type} Ward",
        "mode": "instance",
        "type": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                        "code": "HU",
                        "display": "Hospital Unit"
                    }
                ]
            }
        ],
        "managingOrganization": {
            "reference": f"Organization/{bed.facility_id}"
        },
        "partOf": {
            "display": bed.facility.name
        },
        "extension": [
            {
                "url": "https://swasth.ai/fhir/StructureDefinition/bed-capacity",
                "valueInteger": bed.total_beds
            },
            {
                "url": "https://swasth.ai/fhir/StructureDefinition/bed-occupancy",
                "valueInteger": bed.occupied_beds
            }
        ]
    }

@router.get("/Practitioner/{staff_id}")
def get_fhir_practitioner(
    staff_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    staff = db.query(models.Staff).filter(models.Staff.staff_id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff record not found")
        
    return {
        "resourceType": "Practitioner",
        "id": staff.staff_id,
        "active": staff.is_active,
        "name": [
            {
                "text": staff.name
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": staff.phone or "+91-0000000000"
            },
            {
                "system": "email",
                "value": staff.email or "pending@swasth.ai"
            }
        ],
        "qualification": [
            {
                "code": {
                    "coding": [
                        {
                            "system": "https://swasth.ai/roles",
                            "code": staff.role,
                            "display": staff.role.replace("_", " ").title()
                        }
                    ]
                }
            }
        ]
    }

@router.get("/MedicationStatement/{sku_id}")
def get_fhir_medication_statement(
    sku_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    item = db.query(models.StockItem).filter(models.StockItem.sku_id == sku_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory SKU not found")
        
    return {
        "resourceType": "MedicationStatement",
        "id": item.sku_id,
        "status": "active",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "display": item.medicine_name
                }
            ],
            "text": item.medicine_name
        },
        "subject": {
            "reference": f"Organization/{item.facility_id}"
        },
        "effectiveDateTime": item.last_updated.isoformat() if item.last_updated else datetime.utcnow().isoformat(),
        "note": [
            {
                "text": f"On-hand stock quantity: {item.quantity} {item.unit}. Min threshold: {item.min_threshold}. Max threshold: {item.max_threshold}."
            }
        ]
    }
