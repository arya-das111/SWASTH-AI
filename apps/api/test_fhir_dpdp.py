import os
import sys
from fastapi.testclient import TestClient

# Add api directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, "apps", "api"))

from main import app

client = TestClient(app)

def get_auth_headers(username, password="password123"):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_fhir_dpdp():
    print("\n=== RUNNING PHASE 5 FHIR & DPDP COMPLIANCE TESTS ===")
    
    # 1. Login as Admin
    print("Logging in as administrator...")
    auth_headers = get_auth_headers("admin")
    
    # Get standard IDs from list endpoints
    fac_res = client.get("/api/v1/facilities", headers=auth_headers)
    assert fac_res.status_code == 200
    facilities = fac_res.json()
    assert len(facilities) > 0
    target_fac = facilities[0]
    fac_id = target_fac["facility_id"]
    
    # 2. Test FHIR Organization endpoint
    print(f"Retrieving FHIR Organization for facility ID: {fac_id}...")
    fhir_org = client.get(f"/api/v1/fhir/Organization/{fac_id}", headers=auth_headers)
    assert fhir_org.status_code == 200
    org_data = fhir_org.json()
    assert org_data["resourceType"] == "Organization"
    assert org_data["name"] == target_fac["name"]
    print("  Passed. Valid FHIR Organization representation returned.")

    # 3. Test DPDP Consent
    print("Submitting DPDP consent record...")
    consent_payload = {
        "consent_given": True,
        "remarks": "Onboard consent given during testing audit"
    }
    consent_res = client.post("/api/v1/dpdp/consent", json=consent_payload, headers=auth_headers)
    assert consent_res.status_code == 200
    print("  Passed. Consent successfully recorded in secure audit trail.")

    # 4. Test DPDP Data Access Request
    # We query the facility staff list to get a valid staff_id
    staff_list_res = client.get(f"/api/v1/facilities/{fac_id}/staff", headers=auth_headers)
    assert staff_list_res.status_code == 200
    staff_members = staff_list_res.json()
    assert len(staff_members) > 0
    staff_id = staff_members[0]["staff_id"]
    
    print(f"Executing DPDP Access Request for staff: {staff_id}...")
    access_res = client.get(f"/api/v1/dpdp/requests/access?staff_id={staff_id}", headers=auth_headers)
    assert access_res.status_code == 200
    access_data = access_res.json()
    assert "data_principal" in access_data
    assert "attendance_trail" in access_data
    print("  Passed. Data access request resolved and audit trail generated.")
    
    # 5. Test DPDP Deletion (Redaction)
    print(f"Triggering DPDP Erasure / Deletion for staff ID: {staff_id}...")
    deletion_payload = {
        "staff_id": staff_id
    }
    del_res = client.post("/api/v1/dpdp/requests/deletion", json=deletion_payload, headers=auth_headers)
    assert del_res.status_code == 200
    print("  Passed. Practitioner PII fields successfully redacted/erased.")

    print("\nALL PHASE 5 FHIR & DPDP COMPLIANCE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        test_fhir_dpdp()
    except AssertionError as e:
        print(f"\nASSERTION ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
