import os
import sys
from fastapi.testclient import TestClient

# Add api directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, "apps", "api"))

from main import app
from database import SessionLocal
import models

client = TestClient(app)

def get_auth_headers(username, password="password123"):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_ai_endpoints():
    print("\n=== RUNNING PHASE 3 AI/ML CAPABILITY TESTS ===")
    
    # 1. Login as DHO
    print("Logging in as DHO...")
    dho_headers = get_auth_headers("dho_lucknow")
    
    # Fetch first facility ID
    db = SessionLocal()
    facility = db.query(models.Facility).first()
    facility_id = facility.facility_id
    
    # Fetch a SKU at this facility
    sku = db.query(models.StockItem).filter(models.StockItem.facility_id == facility_id).first()
    sku_id = sku.sku_id
    db.close()
    
    # 2. Compute Scores
    print("Triggering facility scores recomputation...")
    response = client.post("/api/v1/scores/compute", headers=dho_headers)
    assert response.status_code == 200
    print("  Score computation triggered successfully.")
    
    # 3. Retrieve Ranked Scores
    print("Fetching district facility rankings...")
    response = client.get("/api/v1/scores/district", headers=dho_headers)
    assert response.status_code == 200
    scores = response.json()
    assert len(scores) > 0
    assert "composite_score" in scores[0]
    print(f"  Oversight rankings loaded. Top facility: {scores[0]['facility_name']} with score {scores[0]['composite_score']}")
    
    # 4. Retrieve Single Facility Score with Natural Language Explainer
    print(f"Retrieving score details for facility ID: {facility_id}...")
    response = client.get(f"/api/v1/scores/facility/{facility_id}", headers=dho_headers)
    assert response.status_code == 200
    detail = response.json()
    assert "explainer" in detail
    assert "composite_score" in detail
    print(f"  Score: {detail['composite_score']} | Explainer: {detail['explainer']}")
    
    # 5. Generate Redistribution Recommendations
    print("Triggering stock redistribution matcher...")
    response = client.post("/api/v1/recommendations/generate", headers=dho_headers)
    assert response.status_code == 200
    print("  Matcher triggered successfully.")
    
    # 6. Retrieve Recommendations
    print("Retrieving pending transfer recommendations...")
    response = client.get("/api/v1/recommendations?status=pending", headers=dho_headers)
    assert response.status_code == 200
    recos = response.json()
    print(f"  Found {len(recos)} pending transfer recommendations.")
    
    # 7. Approve transfer and assert stock updates
    if len(recos) > 0:
        target_rec = recos[0]
        rec_id = target_rec["rec_id"]
        print(f"Approving transfer recommendation ID: {rec_id}...")
        
        # Query target SKU quantities before
        db = SessionLocal()
        sku_before = db.query(models.StockItem).filter(models.StockItem.sku_id == target_rec["resource_id"]).first()
        qty_before = sku_before.quantity
        db.close()
        
        # Approve
        response = client.post(f"/api/v1/recommendations/{rec_id}/decision?decision=accepted", headers=dho_headers)
        assert response.status_code == 200
        
        # Query target SKU quantities after
        db = SessionLocal()
        sku_after = db.query(models.StockItem).filter(models.StockItem.sku_id == target_rec["resource_id"]).first()
        qty_after = sku_after.quantity
        db.close()
        
        print(f"  Transfer succeeded! Target quantity shift: {qty_before} -> {qty_after} (+{target_rec['quantity']} units)")
        assert qty_after == qty_before + target_rec["quantity"]
        
    # 8. Anomaly Early Warning Scanning
    print("Scanning data streams for early-warning anomalies...")
    response = client.get("/api/v1/anomalies", headers=dho_headers)
    assert response.status_code == 200
    anoms = response.json()
    print(f"  Active anomalies detected: {len(anoms)}")
    if len(anoms) > 0:
        print(f"  Sample anomaly: {anoms[0]['title']} | Message: {anoms[0]['message']}")
        
        # Classify Anomaly (True Positive feedback loop)
        anom_id = anoms[0]["alert_id"]
        print(f"Classifying anomaly ID: {anom_id} as true positive...")
        response = client.post(f"/api/v1/anomalies/{anom_id}/classify?classification=true_positive", headers=dho_headers)
        assert response.status_code == 200
        print("  Anomaly classified and resolved successfully.")
        
    # 9. Stock-out Projection Forecast
    print(f"Retrieving stockout projection for SKU: {sku_id}...")
    response = client.get(f"/api/v1/stock/forecast?facility_id={facility_id}&sku_id={sku_id}", headers=dho_headers)
    assert response.status_code == 200
    fore = response.json()
    assert "days_until_stockout" in fore
    assert "forecast" in fore
    assert len(fore["forecast"]) == 28
    print(f"  Forecast complete. Days until stock-out: {fore['days_until_stockout']} days (Projected date: {fore['projected_stockout_date']})")
    
    # 10. Staffing Recommendation Forecast
    print(f"Retrieving staffing load forecasting for facility: {facility_id}...")
    response = client.get(f"/api/v1/footfall/staffing-recommendation?facility_id={facility_id}", headers=dho_headers)
    assert response.status_code == 200
    staff_reco = response.json()
    assert "doctors" in staff_reco
    assert "nurses" in staff_reco
    print(f"  Staffing Rec -> Doctors: {staff_reco['doctors']['recommended']} (Active now: {staff_reco['doctors']['current_active']}) | Nurses: {staff_reco['nurses']['recommended']} (Active now: {staff_reco['nurses']['current_active']})")

    print("\nALL PHASE 3 AI/ML ENDPOINT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        test_ai_endpoints()
    except AssertionError as e:
        print(f"\nASSERTION ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
