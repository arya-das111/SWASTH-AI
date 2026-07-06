import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
import os
import sys

# Add current path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import models
from database import engine, get_db
from auth import verify_password, create_access_token, get_current_user
from routers import facilities, stock, footfall, beds, attendance, diagnostics, dashboard, forecast, anomalies, recommendations, scores, translate, fhir, dpdp

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Dynamic SQLite migration for geotracking columns
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE attendance_records ADD COLUMN check_in_lat FLOAT"))
        conn.commit()
    except Exception:
        pass
    try:
        conn.execute(text("ALTER TABLE attendance_records ADD COLUMN check_in_lon FLOAT"))
        conn.commit()
    except Exception:
        pass


app = FastAPI(
    title="Swasth AI API",
    description="Backend API service for Swasth AI — AI-driven Health Centre platform",
    version="1.0.0"
)

# Register sub-routers
app.include_router(facilities.router)
app.include_router(stock.router)
app.include_router(footfall.router)
app.include_router(beds.router)
app.include_router(attendance.router)
app.include_router(diagnostics.router)
app.include_router(dashboard.router)
app.include_router(forecast.router)
app.include_router(anomalies.router)
app.include_router(recommendations.router)
app.include_router(scores.router)
app.include_router(translate.router)
app.include_router(fhir.router)
app.include_router(dpdp.router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to verify DB connectivity
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "detail": str(e)}

@app.post("/api/v1/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Generate token
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "facility_id": user.facility_id,
        "district": user.district
    }

@app.get("/api/v1/auth/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "role": current_user.role,
        "facility_id": current_user.facility_id,
        "district": current_user.district,
        "state": current_user.state,
        "language_pref": current_user.language_pref
    }

@app.get("/api/v1/alerts")
def list_alerts(
    status_str: Optional[str] = "active",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Alert)
    
    # If not admin or DHO, restrict to facility
    if current_user.role not in ["dho", "state_admin", "system_admin"]:
        query = query.filter(models.Alert.facility_id == current_user.facility_id)
        
    if status_str:
        query = query.filter(models.Alert.status == status_str)
        
    # Join with facility details for rich UI display
    results = query.order_by(models.Alert.generated_at.desc()).all()
    
    alerts_list = []
    for r in results:
        fac_name = "District-wide"
        if r.facility_id:
            fac = db.query(models.Facility).filter(models.Facility.facility_id == r.facility_id).first()
            if fac:
                fac_name = fac.name
                
        alerts_list.append({
            "alert_id": r.alert_id,
            "facility_id": r.facility_id,
            "facility_name": fac_name,
            "alert_type": r.alert_type,
            "severity": r.severity,
            "title": r.title,
            "message": r.message,
            "status": r.status,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None
        })
        
    return alerts_list

@app.post("/api/v1/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    alert = db.query(models.Alert).filter(models.Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.status = "resolved"
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "success", "message": "Alert marked as resolved"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
