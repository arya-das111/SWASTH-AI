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

def test_translation_offline():
    print("\n=== RUNNING PHASE 4 TRANSLATION & OFFLINE TESTS ===")
    
    # 1. Login as Pharmacist
    print("Logging in as pharmacist...")
    auth_headers = get_auth_headers("pharmacist_phc1")
    
    # 2. Test Static translation lookup (Hindi)
    print("Testing translation lookup for pre-translated UI term (hi-IN)...")
    payload = {
        "text": "Medicine Inventory Ledger",
        "source_lang": "en-IN",
        "target_lang": "hi-IN"
    }
    response = client.post("/api/v1/translate", json=payload, headers=auth_headers)
    assert response.status_code == 200
    translated = response.json()["translated_text"]
    assert translated == "दवा सूची बही"
    print("  Passed. Translated successfully to Devanagari script.")

    # 3. Test Static translation lookup (Tamil)
    print("Testing translation lookup for pre-translated UI term (ta-IN)...")
    payload = {
        "text": "Medicine Inventory Ledger",
        "source_lang": "en-IN",
        "target_lang": "ta-IN"
    }
    response = client.post("/api/v1/translate", json=payload, headers=auth_headers)
    assert response.status_code == 200
    translated = response.json()["translated_text"]
    assert translated == "மருந்து இருப்புப் பதிவேடு"
    print("  Passed. Translated successfully to Tamil script.")

    # 4. Test Dynamic translation fallback (when no Sarvam API key is configured)
    print("Testing dynamic translation fallback for arbitrary text...")
    payload = {
        "text": "The patient needs immediate critical paracetamol care.",
        "source_lang": "en-IN",
        "target_lang": "hi-IN"
    }
    response = client.post("/api/v1/translate", json=payload, headers=auth_headers)
    assert response.status_code == 200
    translated = response.json()["translated_text"]
    assert translated.startswith("[Hindi]")
    print("  Passed. Fallback response resolved successfully.")

    print("\nALL PHASE 4 TRANSLATION & OFFLINE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        test_translation_offline()
    except AssertionError as e:
        print(f"\nASSERTION ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
