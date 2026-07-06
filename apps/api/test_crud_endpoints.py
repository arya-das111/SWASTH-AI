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

def test_crud_endpoints():
    print("\n=== RUNNING PHASE 1 END-TO-END CRUD TESTS ===")
    
    # 1. Login as pharmacist
    print("Logging in as pharmacist...")
    pharma_headers = get_auth_headers("pharmacist_phc1")
    
    # 2. Get list of stock items
    print("Fetching stock items...")
    response = client.get("/api/v1/stock/items", headers=pharma_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    print(f"  Fetched {len(items)} stock items successfully.")
    
    # Choose a stock item to test movements
    target_item = items[0]
    sku_id = target_item["sku_id"]
    current_qty = target_item["quantity"]
    print(f"  Target SKU: {target_item['medicine_name']} (Batch: {target_item['batch_no']}) | Qty: {current_qty}")
    
    # 3. Log a stock movement
    # Move some stock IN
    print("Logging stock IN movement...")
    response = client.post(
        "/api/v1/stock/movements",
        json={"sku_id": sku_id, "movement_type": "in", "quantity": 10, "reference_note": "Test incoming"},
        headers=pharma_headers
    )
    assert response.status_code == 201
    movement = response.json()
    assert movement["quantity"] == 10
    assert movement["movement_type"] == "in"
    print("  Stock IN logged successfully.")
    
    # Verify stock quantity updated
    response = client.get(f"/api/v1/stock/items", headers=pharma_headers)
    updated_item = next(x for x in response.json() if x["sku_id"] == sku_id)
    assert updated_item["quantity"] == current_qty + 10
    print("  Stock quantity successfully updated (+10).")
    
    # Log stock OUT movement that triggers low stock
    print("Logging stock OUT movement that triggers low stock alert...")
    # Update threshold to be just below current quantity + 10, then log out movement to drop below it
    db = SessionLocal()
    db_item = db.query(models.StockItem).filter(models.StockItem.sku_id == sku_id).first()
    db_item.min_threshold = updated_item["quantity"] - 2
    db.commit()
    db.close()
    
    response = client.post(
        "/api/v1/stock/movements",
        json={"sku_id": sku_id, "movement_type": "out", "quantity": 5, "reference_note": "Test drop below threshold"},
        headers=pharma_headers
    )
    assert response.status_code == 201
    print("  Stock OUT logged successfully.")
    
    # Verify low stock alert generated
    db = SessionLocal()
    low_stock_alert = db.query(models.Alert).filter(
        models.Alert.alert_type == "stock_low",
        models.Alert.status == "active"
    ).order_by(models.Alert.generated_at.desc()).first()
    assert low_stock_alert is not None
    assert sku_id in low_stock_alert.extra_metadata["sku_id"]
    print(f"  Low stock alert successfully triggered: '{low_stock_alert.title}'.")
    db.close()

    # 4. Login as nurse
    print("Logging in as nurse...")
    nurse_headers = get_auth_headers("nurse_phc1")
    
    # 5. Log footfall
    print("Logging daily patient footfall...")
    response = client.post(
        "/api/v1/footfall",
        json={"department": "General", "opd_count": 85, "ipd_count": 5},
        headers=nurse_headers
    )
    assert response.status_code == 201
    record = response.json()
    assert record["opd_count"] == 85
    assert record["ipd_count"] == 5
    print("  Patient footfall logged successfully.")

    # 6. Log bed status
    print("Logging bed occupancy status (triggering high occupancy alert >85%)...")
    response = client.post(
        "/api/v1/beds/status",
        json={"ward_type": "General", "total_beds": 10, "occupied_beds": 9},
        headers=nurse_headers
    )
    assert response.status_code == 201
    print("  Bed status logged successfully.")
    
    # Verify bed alert triggered
    db = SessionLocal()
    bed_alert = db.query(models.Alert).filter(
        models.Alert.alert_type == "bed_capacity",
        models.Alert.status == "active"
    ).order_by(models.Alert.generated_at.desc()).first()
    assert bed_alert is not None
    assert bed_alert.extra_metadata["occupancy_rate"] == 90.0
    print(f"  High bed occupancy alert successfully triggered: '{bed_alert.title}'.")
    db.close()

    # 7. Log diagnostic audit
    print("Submitting diagnostic audit check...")
    # Fetch first diagnostic test
    tests_res = client.get("/api/v1/diagnostics/tests", headers=nurse_headers)
    assert tests_res.status_code == 200
    test_id = tests_res.json()[0]["test_id"]
    
    response = client.post(
        "/api/v1/diagnostics/audit",
        json={"test_id": test_id, "status": "available", "reagent_stock": 250, "notes": "Tested ok"},
        headers=nurse_headers
    )
    assert response.status_code == 201
    print("  Diagnostic audit logged successfully.")

    # 8. Log in as DHO for overview APIs
    print("Logging in as DHO...")
    dho_headers = get_auth_headers("dho_lucknow")
    
    # 9. Test District Heatmap
    print("Fetching district stock heatmap...")
    response = client.get("/api/v1/stock/district-heatmap", headers=dho_headers)
    assert response.status_code == 200
    heatmap = response.json()
    assert len(heatmap["medicines"]) > 0
    assert len(heatmap["matrix"]) > 0
    print("  District stock heatmap fetched successfully.")
    
    # 10. Test Bed Availability Redirection
    print("Fetching bed redirection availability...")
    response = client.get(
        "/api/v1/beds/availability",
        params={"ward_type": "General"},
        headers=dho_headers
    )
    assert response.status_code == 200
    redirects = response.json()
    print(f"  Found {len(redirects)} available redirect facilities.")
    
    # 11. Test Coverage Gaps
    print("Fetching district coverage gaps...")
    response = client.get("/api/v1/attendance/gaps", headers=dho_headers)
    assert response.status_code == 200
    print("  District coverage gaps fetched successfully.")

    # 12. Test Diagnostics Compliance Gaps
    print("Fetching FDSI diagnostics compliance gaps...")
    response = client.get("/api/v1/diagnostics/mandated-gaps", headers=dho_headers)
    assert response.status_code == 200
    print("  Diagnostics gaps fetched successfully.")
    
    print("\nALL PHASE 1 CRUD INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        test_crud_endpoints()
    except AssertionError as e:
        print(f"\nASSERTION ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
