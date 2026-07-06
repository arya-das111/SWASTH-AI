import os
import sys
from fastapi.testclient import TestClient

# Add api directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(BASE_DIR, "apps", "api"))

from main import app

client = TestClient(app)

def test_health_endpoint():
    print("Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    print("  /health passed!")

def test_login_success():
    print("Testing successful login...")
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "dho_lucknow", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "dho"
    print("  Login success passed!")
    return data["access_token"]

def test_login_failure():
    print("Testing failed login...")
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "dho_lucknow", "password": "wrong_password"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Incorrect username or password"
    print("  Login failure passed!")

def test_get_me(token):
    print("Testing /auth/me with valid token...")
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "dho_lucknow"
    assert data["role"] == "dho"
    assert data["district"] == "Lucknow"
    print("  /auth/me passed!")

def test_get_me_invalid_token():
    print("Testing /auth/me with invalid token...")
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    assert response.status_code == 401
    print("  /auth/me invalid token passed!")

if __name__ == "__main__":
    print("\n=== RUNNING AUTH & INTEGRATION TESTS ===")
    try:
        test_health_endpoint()
        token = test_login_success()
        test_login_failure()
        test_get_me(token)
        test_get_me_invalid_token()
        print("\nALL API INTEGRATION TESTS PASSED SUCCESSFULLY!")
    except AssertionError as e:
        print(f"\nASSERTION ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        sys.exit(1)
