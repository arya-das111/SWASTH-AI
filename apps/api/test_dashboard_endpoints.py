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

def test_dashboard_endpoints():
    print("\n=== RUNNING PHASE 2 DASHBOARD AGGREGATION TESTS ===")
    
    # 1. Login as DHO
    print("Logging in as DHO...")
    dho_headers = get_auth_headers("dho_lucknow")
    
    # Get a facility ID to query
    db = SessionLocal()
    facility = db.query(models.Facility).first()
    facility_id = facility.facility_id
    db.close()
    
    # 2. Query Facility Dashboard Aggregator
    print(f"Querying facility dashboard aggregator for ID: {facility_id}...")
    response = client.get(f"/api/v1/dashboard/facility/{facility_id}", headers=dho_headers)
    assert response.status_code == 200
    fac_data = response.json()
    
    assert "stock" in fac_data
    assert "beds" in fac_data
    assert "attendance" in fac_data
    assert "diagnostics" in fac_data
    assert "footfall" in fac_data
    assert "composite_score" in fac_data
    print("  Facility dashboard aggregator PASSED.")

    # 3. Query District Dashboard Aggregator
    print("Querying district dashboard aggregator...")
    response = client.get("/api/v1/dashboard/district", headers=dho_headers)
    assert response.status_code == 200
    dist_data = response.json()
    
    assert dist_data["district"] == "Lucknow"
    assert dist_data["total_facilities"] == 25
    assert "beds" in dist_data
    assert "attendance" in dist_data
    assert "alerts" in dist_data
    print("  District dashboard aggregator PASSED.")
    
    # 4. Login as State Admin
    print("Logging in as State Admin...")
    state_headers = get_auth_headers("admin")
    
    # 5. Query State Dashboard Aggregator
    print("Querying state dashboard aggregator (Uttar Pradesh leaderboard)...")
    response = client.get("/api/v1/dashboard/state", headers=state_headers)
    assert response.status_code == 200
    state_data = response.json()
    
    assert state_data["state"] == "Uttar Pradesh"
    assert state_data["total_districts"] == 4
    assert len(state_data["districts"]) == 4
    print("  State dashboard aggregator PASSED.")

    print("\nALL PHASE 2 DASHBOARD AGGREGATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        test_dashboard_endpoints()
    except AssertionError as e:
        print(f"\nASSERTION ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
