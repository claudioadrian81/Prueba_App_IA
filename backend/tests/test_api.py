from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers():
    email = "test@example.com"
    password = "secret123"
    client.post("/api/auth/register", json={"email": email, "password": password})
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_analyze_and_summary_flow():
    headers = auth_headers()
    fake_image = BytesIO(b"fake-image-data")
    files = {"image": ("mixed_plate.jpg", fake_image, "image/jpeg")}

    analyze = client.post("/api/meals/analyze", files=files, headers=headers)
    assert analyze.status_code == 200
    meal_id = analyze.json()["meal_id"]

    meal = client.get(f"/api/meals/{meal_id}", headers=headers)
    assert meal.status_code == 200
    assert meal.json()["items"]

    summary = client.get("/api/meals/daily/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["total_calories"] >= 0
