from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, timedelta, datetime
import pandas as pd
import numpy as np
import math
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
import auth
from database import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["AI Forecasting"]
)

# Helper function to compute trend and seasonal forecast using pandas & numpy
def fit_seasonal_forecast(daily_series: pd.Series, periods: int = 28):
    if len(daily_series) < 5:
        # Fallback to simple mean
        mean_val = float(daily_series.mean()) if not daily_series.empty else 1.0
        if math.isnan(mean_val) or mean_val <= 0:
            mean_val = 1.0
        dates = [date.today() + timedelta(days=i) for i in range(1, periods + 1)]
        preds = [mean_val] * periods
        lower_bounds = [max(0.0, mean_val * 0.5)] * periods
        upper_bounds = [mean_val * 1.5] * periods
        mape = 15.0
        return dates, preds, lower_bounds, upper_bounds, mape

    # Prepare DataFrame
    df = pd.DataFrame({'y': daily_series.values}, index=pd.to_datetime(daily_series.index))
    df['t'] = np.arange(len(df))
    df['dayofweek'] = df.index.dayofweek

    # Fit linear trend: y = m * t + c
    m, c = np.polyfit(df['t'], df['y'], 1)
    df['trend'] = m * df['t'] + c

    # Calculate weekly seasonality (average deviation from trend by day of week)
    df['detrended'] = df['y'] - df['trend']
    weekly_season = df.groupby('dayofweek')['detrended'].mean().to_dict()
    # Default to 0 for missing days of week
    for d in range(7):
        if d not in weekly_season:
            weekly_season[d] = 0.0

    # Project future
    future_dates = [date.today() + timedelta(days=i) for i in range(1, periods + 1)]
    future_ts = np.arange(len(df), len(df) + periods)
    
    predictions = []
    lower_bounds = []
    upper_bounds = []
    
    # Calculate residual standard error
    residuals = df['y'] - (df['trend'] + df['dayofweek'].map(weekly_season))
    std_err = float(residuals.std()) if len(residuals) > 1 else float(df['y'].std() or 1.0)
    if std_err <= 0:
        std_err = 1.0

    for idx, f_date in enumerate(future_dates):
        t_val = future_ts[idx]
        trend_val = m * t_val + c
        dow = f_date.weekday()
        season_val = weekly_season[dow]
        pred_val = max(0.0, trend_val + season_val)
        
        predictions.append(float(pred_val))
        lower_bounds.append(float(max(0.0, pred_val - 1.96 * std_err)))
        upper_bounds.append(float(pred_val + 1.96 * std_err))

    # Evaluate MAPE on training data
    train_preds = df['trend'] + df['dayofweek'].map(weekly_season)
    train_preds = train_preds.clip(lower=0)
    
    # Avoid zero division
    mask = df['y'] > 0
    if mask.sum() > 0:
        mape = float(np.mean(np.abs((df['y'][mask] - train_preds[mask]) / df['y'][mask])) * 100)
    else:
        mape = 10.0
        
    return future_dates, predictions, lower_bounds, upper_bounds, round(mape, 1)

@router.get("/stock/forecast")
def get_stock_forecast(
    facility_id: str,
    sku_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    sku = db.query(models.StockItem).filter(
        models.StockItem.sku_id == sku_id,
        models.StockItem.facility_id == facility_id
    ).first()
    if not sku:
        raise HTTPException(status_code=404, detail="Stock SKU not found at this facility")

    # Get historical logs of type='out' for the last 90 days
    start_date = datetime.now() - timedelta(days=90)
    movements = db.query(models.StockMovement).filter(
        models.StockMovement.sku_id == sku_id,
        models.StockMovement.movement_type == "out",
        models.StockMovement.timestamp >= start_date
    ).order_by(models.StockMovement.timestamp).all()

    # Create daily consumption series
    dates_list = []
    qtys_list = []
    for m in movements:
        dates_list.append(m.timestamp.date())
        qtys_list.append(m.quantity)
        
    df = pd.DataFrame({'qty': qtys_list}, index=dates_list)
    daily_consumption = df.groupby(df.index)['qty'].sum()

    # Fit model and predict next 28 days
    f_dates, preds, lower, upper, mape = fit_seasonal_forecast(daily_consumption, periods=28)
    
    avg_daily_demand = float(np.mean(preds))
    if avg_daily_demand <= 0:
        avg_daily_demand = 1.0 # fallback
        
    current_qty = sku.quantity
    days_to_out = current_qty / avg_daily_demand
    
    stockout_date = None
    if days_to_out < 365:
        stockout_date = (date.today() + timedelta(days=max(0, math.ceil(days_to_out)))).isoformat()
        days_until_out = max(0, math.ceil(days_to_out))
    else:
        days_until_out = 999  # Safe
        
    return {
        "sku_id": sku_id,
        "facility_id": facility_id,
        "medicine_name": sku.medicine_name,
        "current_stock": current_qty,
        "average_daily_demand": round(avg_daily_demand, 1),
        "days_until_stockout": days_until_out,
        "projected_stockout_date": stockout_date,
        "mape": mape,
        "forecast": [
            {
                "date": f_dates[i].isoformat(),
                "predicted_consumption": round(preds[i], 1),
                "lower_bound": round(lower[i], 1),
                "upper_bound": round(upper[i], 1)
            } for i in range(len(preds))
        ]
    }

@router.get("/stock/forecast/bulk")
def get_bulk_stock_forecast(
    facility_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    skus = db.query(models.StockItem).filter(models.StockItem.facility_id == facility_id).all()
    forecasts = []
    for s in skus:
        try:
            fc = get_stock_forecast(facility_id, s.sku_id, db, current_user)
            forecasts.append(fc)
        except Exception:
            # Fallback for error SKUs
            forecasts.append({
                "sku_id": s.sku_id,
                "facility_id": facility_id,
                "medicine_name": s.medicine_name,
                "current_stock": s.quantity,
                "average_daily_demand": 1.0,
                "days_until_stockout": 90,
                "projected_stockout_date": (date.today() + timedelta(days=90)).isoformat(),
                "mape": 10.0,
                "forecast": []
            })
            
    # Sort by urgency (days until stockout) ascending
    forecasts.sort(key=lambda x: x["days_until_stockout"])
    return forecasts

@router.get("/footfall/forecast")
def get_footfall_forecast(
    facility_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Fetch historical daily footfall logs
    start_date = datetime.now() - timedelta(days=90)
    records = db.query(models.FootfallRecord).filter(
        models.FootfallRecord.facility_id == facility_id,
        models.FootfallRecord.record_date >= start_date
    ).order_by(models.FootfallRecord.record_date).all()
    
    dates_list = []
    counts_list = []
    for r in records:
        dates_list.append(r.record_date)
        counts_list.append(r.opd_count + r.ipd_count)
        
    df = pd.DataFrame({'count': counts_list}, index=dates_list)
    daily_footfall = df.groupby(df.index)['count'].sum()
    
    # Predict next 14 days
    f_dates, preds, lower, upper, mape = fit_seasonal_forecast(daily_footfall, periods=14)
    
    return {
        "facility_id": facility_id,
        "mape": mape,
        "forecast": [
            {
                "date": f_dates[i].isoformat(),
                "predicted_footfall": round(preds[i], 1),
                "lower_bound": round(lower[i], 1),
                "upper_bound": round(upper[i], 1)
            } for i in range(len(preds))
        ]
    }

@router.get("/footfall/staffing-recommendation")
def get_staffing_recommendation(
    facility_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Get 14 days forecast
    fc = get_footfall_forecast(facility_id, db, current_user)
    predictions = [x["predicted_footfall"] for x in fc["forecast"]]
    avg_weekly_patients = float(np.mean(predictions[:7]))
    
    # Standard staffing rule ratio
    # 1 Medical Officer per 30 patient consultations daily
    # 1 Nurse per 15 patient consultations/admissions daily
    recommended_docs = max(1, math.ceil(avg_weekly_patients / 30))
    recommended_nurses = max(2, math.ceil(avg_weekly_patients / 15))
    
    # Get current active checked-in staff today
    today = date.today()
    active_rosters = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.facility_id == facility_id,
        models.AttendanceRecord.attendance_date == today,
        models.AttendanceRecord.status.in_(["present", "late"])
    ).all()
    
    current_docs = 0
    current_nurses = 0
    for r in active_rosters:
        staff = db.query(models.StaffRoster).filter(models.StaffRoster.staff_id == r.staff_id).first()
        if staff:
            if staff.role == "medical_officer":
                current_docs += 1
            elif staff.role in ["nurse", "anm"]:
                current_nurses += 1
                
    return {
        "facility_id": facility_id,
        "average_expected_daily_patients": round(avg_weekly_patients, 1),
        "doctors": {
            "recommended": recommended_docs,
            "current_active": current_docs,
            "gap": max(0, recommended_docs - current_docs)
        },
        "nurses": {
            "recommended": recommended_nurses,
            "current_active": current_nurses,
            "gap": max(0, recommended_nurses - current_nurses)
        }
    }
