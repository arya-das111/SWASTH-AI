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
    prefix="/api/v1/stock",
    tags=["Stock Inventory"]
)

# Role check dependencies
pharmacist_or_mo = auth.RoleChecker(["pharmacist", "medical_officer", "system_admin"])

@router.get("/items")
def list_stock_items(
    facility_id: Optional[str] = None,
    category: Optional[str] = None,
    below_threshold: Optional[bool] = None,
    expiring_soon: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.StockItem)
    
    # If not admin/dho, restrict to own facility
    if current_user.role not in ["dho", "state_admin", "system_admin"]:
        if not current_user.facility_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not assigned to a facility"
            )
        query = query.filter(models.StockItem.facility_id == current_user.facility_id)
    elif facility_id:
        query = query.filter(models.StockItem.facility_id == facility_id)
        
    if category:
        query = query.filter(models.StockItem.category == category)
        
    if below_threshold:
        query = query.filter(models.StockItem.quantity < models.StockItem.min_threshold)
        
    if expiring_soon:
        target_date = date.today() + timedelta(days=30)
        query = query.filter(models.StockItem.expiry_date <= target_date, models.StockItem.expiry_date >= date.today())
        
    return query.all()

@router.post("/items", status_code=status.HTTP_201_CREATED)
def register_stock_item(
    item_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(pharmacist_or_mo)
):
    # Enforce facility scoping if not admin
    facility_id = item_data.get("facility_id")
    if current_user.role not in ["system_admin", "dho"]:
        facility_id = current_user.facility_id
        
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility ID is required"
        )
        
    required = ["medicine_name", "unit", "quantity"]
    for field in required:
        if field not in item_data or item_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' is required"
            )
            
    # Check duplicate batch
    batch_no = item_data.get("batch_no")
    if batch_no:
        existing = db.query(models.StockItem).filter(
            models.StockItem.facility_id == facility_id,
            models.StockItem.medicine_name == item_data["medicine_name"],
            models.StockItem.batch_no == batch_no
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item with batch '{batch_no}' already registered"
            )
            
    expiry = None
    if item_data.get("expiry_date"):
        expiry = date.fromisoformat(item_data["expiry_date"])
        
    item = models.StockItem(
        facility_id=facility_id,
        medicine_name=item_data["medicine_name"],
        generic_name=item_data.get("generic_name"),
        category=item_data.get("category"),
        unit=item_data["unit"],
        batch_no=batch_no,
        quantity=item_data["quantity"],
        expiry_date=expiry,
        min_threshold=item_data.get("min_threshold", 50),
        max_threshold=item_data.get("max_threshold", 500)
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    # Auto-alert triggers on initial register if quantity is low
    if item.quantity == 0:
        alert = models.Alert(
            facility_id=item.facility_id,
            alert_type="stock_out",
            severity="critical",
            title=f"Stockout: {item.medicine_name}",
            message=f"Medicine '{item.medicine_name}' is completely out of stock.",
            status="active",
            routed_to_role="pharmacist",
            extra_metadata={"sku_id": item.sku_id, "medicine_name": item.medicine_name}
        )
        db.add(alert)
        db.commit()
    elif item.quantity < item.min_threshold:
        alert = models.Alert(
            facility_id=item.facility_id,
            alert_type="stock_low",
            severity="high",
            title=f"Low Stock: {item.medicine_name}",
            message=f"Medicine '{item.medicine_name}' is below threshold. Current: {item.quantity}.",
            status="active",
            routed_to_role="pharmacist",
            extra_metadata={"sku_id": item.sku_id, "medicine_name": item.medicine_name}
        )
        db.add(alert)
        db.commit()
        
    return item

@router.post("/movements", status_code=status.HTTP_201_CREATED)
def log_stock_movement(
    movement_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    required = ["sku_id", "movement_type", "quantity"]
    for field in required:
        if field not in movement_data or not movement_data[field]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Field '{field}' is required"
            )
            
    # Verify stock item exists
    item = db.query(models.StockItem).filter(models.StockItem.sku_id == movement_data["sku_id"]).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock item (SKU) not found"
        )
        
    # Enforce facility mapping for pharmacists
    if current_user.role not in ["dho", "system_admin"] and item.facility_id != current_user.facility_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only log movements for your own facility's stock"
        )
        
    qty = movement_data["quantity"]
    m_type = movement_data["movement_type"]
    
    # Recalculate quantity
    if m_type in ["out", "expired", "wastage"]:
        if item.quantity < qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {item.quantity}, Requested: {qty}"
            )
        item.quantity -= qty
    elif m_type in ["in", "transfer"]:
        item.quantity += qty
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid movement type '{m_type}'"
        )
        
    movement = models.StockMovement(
        sku_id=item.sku_id,
        facility_id=item.facility_id,
        movement_type=m_type,
        quantity=qty,
        batch_no=item.batch_no,
        reference_note=movement_data.get("reference_note"),
        user_id=current_user.staff_id or current_user.user_id
    )
    db.add(movement)
    
    # Check trigger rules for alerts
    if item.quantity == 0:
        alert = models.Alert(
            facility_id=item.facility_id,
            alert_type="stock_out",
            severity="critical",
            title=f"Stockout: {item.medicine_name}",
            message=f"Medicine '{item.medicine_name}' (Batch: {item.batch_no}) has run out completely at this facility.",
            status="active",
            routed_to_role="pharmacist",
            extra_metadata={"sku_id": item.sku_id, "medicine_name": item.medicine_name}
        )
        db.add(alert)
    elif item.quantity < item.min_threshold:
        # Check if alert already active to prevent duplicates
        active_alert = db.query(models.Alert).filter(
            models.Alert.facility_id == item.facility_id,
            models.Alert.alert_type == "stock_low",
            models.Alert.status == "active",
            models.Alert.title.contains(item.medicine_name)
        ).first()
        if not active_alert:
            alert = models.Alert(
                facility_id=item.facility_id,
                alert_type="stock_low",
                severity="high",
                title=f"Low Stock: {item.medicine_name}",
                message=f"Medicine '{item.medicine_name}' is below threshold. Current: {item.quantity}, Min: {item.min_threshold}.",
                status="active",
                routed_to_role="pharmacist",
                extra_metadata={"sku_id": item.sku_id, "medicine_name": item.medicine_name}
            )
            db.add(alert)
            
    db.commit()
    db.refresh(movement)
    return movement

@router.get("/summary")
def get_stock_summary(
    facility_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    fid = facility_id
    if current_user.role not in ["dho", "state_admin", "system_admin"]:
        fid = current_user.facility_id
        
    query = db.query(models.StockItem)
    if fid:
        query = query.filter(models.StockItem.facility_id == fid)
        
    items = query.all()
    total_skus = len(items)
    below_t = sum(1 for x in items if x.quantity < x.min_threshold and x.quantity > 0)
    stockout = sum(1 for x in items if x.quantity == 0)
    
    target_date = date.today() + timedelta(days=30)
    expiring = sum(1 for x in items if x.expiry_date and x.expiry_date <= target_date and x.expiry_date >= date.today())
    
    return {
        "total_skus": total_skus,
        "below_threshold": below_t,
        "stockouts": stockout,
        "expiring_soon": expiring,
        "adequate": total_skus - below_t - stockout
    }

@router.get("/district-heatmap")
def get_district_stock_heatmap(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.RoleChecker(["dho", "state_admin", "system_admin"]))
):
    # Aggregated district matrix
    # Select key critical medicines and map availability per facility
    facilities = db.query(models.Facility).filter(models.Facility.district == "Lucknow").all()
    
    # We will pick 5 representative medicines to make a heatmap matrix
    key_medicines = ["Paracetamol 500mg", "Amoxicillin 250mg", "ORS Powder 20.5g", "Artesunate 60mg", "Metformin 500mg"]
    
    matrix = []
    for f in facilities:
        row = {
            "facility_id": f.facility_id,
            "facility_name": f.name,
            "type": f.type,
            "block": f.block
        }
        for med in key_medicines:
            # Query stock level
            item = db.query(models.StockItem).filter(
                models.StockItem.facility_id == f.facility_id,
                models.StockItem.medicine_name == med
            ).first()
            if not item:
                status_str = "no_stock"  # Not registered
                qty = 0
            elif item.quantity == 0:
                status_str = "stockout"
                qty = 0
            elif item.quantity < item.min_threshold:
                status_str = "low"
                qty = item.quantity
            else:
                status_str = "adequate"
                qty = item.quantity
                
            row[med] = {
                "status": status_str,
                "quantity": qty
            }
        matrix.append(row)
        
    return {
        "medicines": key_medicines,
        "matrix": matrix
    }
