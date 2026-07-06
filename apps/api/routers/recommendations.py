from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import math
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["Redistribution Engine"]
)

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Earth radius in km
    R = 6371.0
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

@router.post("/generate")
def generate_recommendations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    # 1. Gather all stock items
    stock_items = db.query(models.StockItem).all()
    
    # 2. Compute consumption rates and classify surplus vs deficit
    # Group SKUs by medicine_name
    deficits = []
    surpluses = []
    
    for s in stock_items:
        # Compute avg consumption (fallback to 10 if no movements)
        movements = db.query(models.StockMovement).filter(
            models.StockMovement.sku_id == s.sku_id,
            models.StockMovement.movement_type == "out"
        ).all()
        
        total_moved = sum(m.quantity for m in movements)
        avg_rate = total_moved / 30.0 if movements else 10.0
        if avg_rate <= 0:
            avg_rate = 1.0
            
        days_to_out = s.quantity / avg_rate
        
        if days_to_out < 7 or s.quantity < s.min_threshold:
            deficits.append({
                "sku": s,
                "days_to_out": days_to_out,
                "deficit_qty": s.max_threshold - s.quantity,
                "avg_rate": avg_rate
            })
        elif days_to_out > 30 and s.quantity > s.max_threshold:
            surpluses.append({
                "sku": s,
                "days_to_out": days_to_out,
                "surplus_qty": s.quantity - s.min_threshold,
                "avg_rate": avg_rate
            })
            
    recs_created = 0
    
    # 3. Match Surplus to Deficits
    for d in deficits:
        deficit_sku = d["sku"]
        deficit_fac = db.query(models.Facility).filter(models.Facility.facility_id == deficit_sku.facility_id).first()
        if not deficit_fac:
            continue
            
        # Find candidates of same drug
        candidates = [s for s in surpluses if s["sku"].medicine_name == deficit_sku.medicine_name]
        
        for c in candidates:
            surplus_sku = c["sku"]
            if surplus_sku.facility_id == deficit_sku.facility_id:
                continue
                
            surplus_fac = db.query(models.Facility).filter(models.Facility.facility_id == surplus_sku.facility_id).first()
            if not surplus_fac:
                continue
                
            # Calculate distance
            dist = haversine_distance(
                deficit_fac.latitude, deficit_fac.longitude,
                surplus_fac.latitude, surplus_fac.longitude
            )
            
            # Max 50km constraint
            if dist <= 50.0:
                # Calculate transfer amount
                transfer_qty = min(int(c["surplus_qty"]), int(d["deficit_qty"]))
                if transfer_qty <= 0:
                    continue
                    
                # Compute Urgency
                urgency = max(0.0, min(100.0, 100.0 - (d["days_to_out"] * 10.0)))
                
                # Check if recommendation already exists
                title = f"Transfer {deficit_sku.medicine_name} from {surplus_fac.name} to {deficit_fac.name}"
                existing = db.query(models.Recommendation).filter(
                    models.Recommendation.source_facility_id == surplus_fac.facility_id,
                    models.Recommendation.target_facility_id == deficit_fac.facility_id,
                    models.Recommendation.resource_id == deficit_sku.sku_id,
                    models.Recommendation.status == "pending"
                ).first()
                
                if not existing:
                    rationale = (
                        f"{deficit_fac.name} is running critically low on {deficit_sku.medicine_name} "
                        f"({deficit_sku.quantity} remaining, projected stock-out in {round(d['days_to_out'], 1)} days). "
                        f"{surplus_fac.name} has a surplus of {surplus_sku.quantity} units (supply is safe for {round(c['days_to_out'], 1)} days). "
                        f"Transferring {transfer_qty} units resolves the deficit and extends supply by "
                        f"{round(transfer_qty / d['avg_rate'], 1)} days."
                    )
                    
                    rec = models.Recommendation(
                        source_facility_id=surplus_fac.facility_id,
                        target_facility_id=deficit_fac.facility_id,
                        resource_type="medicine",
                        resource_id=deficit_sku.sku_id,
                        quantity=transfer_qty,
                        rationale=rationale,
                        urgency_score=urgency,
                        distance_km=round(dist, 1),
                        status="pending"
                    )
                    db.add(rec)
                    recs_created += 1
                    
    if recs_created > 0:
        db.commit()
        
    return {"status": "success", "message": f"Generated {recs_created} new redistribution recommendations."}

@router.get("")
def list_recommendations(
    status: Optional[str] = "pending",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Auto-generate on load if list is empty
    existing_count = db.query(models.Recommendation).filter(models.Recommendation.status == "pending").count()
    if existing_count == 0:
        # Safely trigger generate logic internally (using current_user role validation check bypass internally)
        # Gather SKUs
        stock_items = db.query(models.StockItem).all()
        deficits = []
        surpluses = []
        for s in stock_items:
            movements = db.query(models.StockMovement).filter(models.StockMovement.sku_id == s.sku_id, models.StockMovement.movement_type == "out").all()
            total_moved = sum(m.quantity for m in movements)
            avg_rate = total_moved / 30.0 if movements else 10.0
            if avg_rate <= 0: avg_rate = 1.0
            days_to_out = s.quantity / avg_rate
            if days_to_out < 7 or s.quantity < s.min_threshold:
                deficits.append({"sku": s, "days_to_out": days_to_out, "deficit_qty": s.max_threshold - s.quantity, "avg_rate": avg_rate})
            elif days_to_out > 30 and s.quantity > s.max_threshold:
                surpluses.append({"sku": s, "days_to_out": days_to_out, "surplus_qty": s.quantity - s.min_threshold, "avg_rate": avg_rate})
                
        for d in deficits:
            deficit_sku = d["sku"]
            deficit_fac = db.query(models.Facility).filter(models.Facility.facility_id == deficit_sku.facility_id).first()
            if not deficit_fac: continue
            candidates = [s for s in surpluses if s["sku"].medicine_name == deficit_sku.medicine_name]
            for c in candidates:
                surplus_sku = c["sku"]
                if surplus_sku.facility_id == deficit_sku.facility_id: continue
                surplus_fac = db.query(models.Facility).filter(models.Facility.facility_id == surplus_sku.facility_id).first()
                if not surplus_fac: continue
                dist = haversine_distance(deficit_fac.latitude, deficit_fac.longitude, surplus_fac.latitude, surplus_fac.longitude)
                if dist <= 50.0:
                    transfer_qty = min(int(c["surplus_qty"]), int(d["deficit_qty"]))
                    if transfer_qty <= 0: continue
                    urgency = max(0.0, min(100.0, 100.0 - (d["days_to_out"] * 10.0)))
                    rationale = f"{deficit_fac.name} is running critically low on {deficit_sku.medicine_name} ({deficit_sku.quantity} remaining, projected stock-out in {round(d['days_to_out'], 1)} days). {surplus_fac.name} has a surplus of {surplus_sku.quantity} units (supply is safe for {round(c['days_to_out'], 1)} days). Transferring {transfer_qty} units resolves the deficit and extends supply by {round(transfer_qty / d['avg_rate'], 1)} days."
                    rec = models.Recommendation(
                        source_facility_id=surplus_fac.facility_id,
                        target_facility_id=deficit_fac.facility_id,
                        resource_type="medicine",
                        resource_id=deficit_sku.sku_id,
                        quantity=transfer_qty,
                        rationale=rationale,
                        urgency_score=urgency,
                        distance_km=round(dist, 1),
                        status="pending"
                    )
                    db.add(rec)
        db.commit()

    query = db.query(models.Recommendation)
    if status:
        query = query.filter(models.Recommendation.status == status)
        
    results = query.order_by(models.Recommendation.urgency_score.desc()).all()
    
    recs_list = []
    for r in results:
        src_name = "Facility A"
        dest_name = "Facility B"
        resource_name = "Resource"
        
        src = db.query(models.Facility).filter(models.Facility.facility_id == r.source_facility_id).first()
        if src:
            src_name = src.name
            
        dest = db.query(models.Facility).filter(models.Facility.facility_id == r.target_facility_id).first()
        if dest:
            dest_name = dest.name
            
        sku = db.query(models.StockItem).filter(models.StockItem.sku_id == r.resource_id).first()
        if sku:
            resource_name = sku.medicine_name
            
        recs_list.append({
            "rec_id": r.rec_id,
            "source_facility_id": r.source_facility_id,
            "source_facility_name": src_name,
            "target_facility_id": r.target_facility_id,
            "target_facility_name": dest_name,
            "resource_type": r.resource_type,
            "resource_id": r.resource_id,
            "resource_name": resource_name,
            "quantity": r.quantity,
            "rationale": r.rationale,
            "urgency_score": float(r.urgency_score) if r.urgency_score else 50.0,
            "distance_km": float(r.distance_km) if r.distance_km else 0.0,
            "status": r.status,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None
        })
        
    return recs_list

@router.post("/{rec_id}/decision")
def make_recommendation_decision(
    rec_id: str,
    decision: str,  # 'accepted' or 'rejected'
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    rec = db.query(models.Recommendation).filter(
        models.Recommendation.rec_id == rec_id,
        models.Recommendation.status == "pending"
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Pending recommendation not found")
        
    if decision not in ["accepted", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid decision. Must be accepted or rejected")
        
    rec.status = decision
    rec.decided_at = datetime.utcnow()
    
    # If accepted, we simulate the actual movement log in the database!
    # This closes the operational loop completely, logging stock deduction at source and addition at target!
    if decision == "accepted":
        sku_deficit = db.query(models.StockItem).filter(models.StockItem.sku_id == rec.resource_id).first()
        if sku_deficit:
            # Find the equivalent stock item at the source facility
            sku_source = db.query(models.StockItem).filter(
                models.StockItem.facility_id == rec.source_facility_id,
                models.StockItem.medicine_name == sku_deficit.medicine_name
            ).first()
            
            if sku_source:
                # Deduct from source
                sku_source.quantity = max(0, sku_source.quantity - rec.quantity)
                # Add to target
                sku_deficit.quantity += rec.quantity
                
                # Log movements
                mov_out = models.StockMovement(
                    sku_id=sku_source.sku_id,
                    facility_id=rec.source_facility_id,
                    movement_type="out",
                    quantity=rec.quantity,
                    reference_note=f"Redistribution transfer TO {sku_deficit.facility.name} (Rec: {rec_id})",
                    user_id=current_user.staff_id or current_user.user_id
                )
                mov_in = models.StockMovement(
                    sku_id=sku_deficit.sku_id,
                    facility_id=rec.target_facility_id,
                    movement_type="in",
                    quantity=rec.quantity,
                    reference_note=f"Redistribution transfer FROM {sku_source.facility.name} (Rec: {rec_id})",
                    user_id=current_user.staff_id or current_user.user_id
                )
                db.add(mov_out)
                db.add(mov_in)
                
    db.commit()
    return {"status": "success", "message": f"Recommendation has been {decision}."}

@router.get("/stats")
def get_recommendations_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    recs = db.query(models.Recommendation).all()
    
    total = len(recs)
    accepted = sum(1 for x in recs if x.status == "accepted")
    rejected = sum(1 for x in recs if x.status == "rejected")
    pending = sum(1 for x in recs if x.status == "pending")
    
    acceptance_rate = (accepted / (accepted + rejected) * 100) if (accepted + rejected) > 0 else 100.0
    
    return {
        "total_recommendations": total,
        "accepted": accepted,
        "rejected": rejected,
        "pending": pending,
        "acceptance_rate_percent": round(acceptance_rate, 1)
    }
