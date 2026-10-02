import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authenticated_user(client):
    email = f"booking_test_{uuid.uuid4().hex}@example.com"
    password = "TestPassword123!"

    response = client.post(
        "/auth/signup",
        json={
            "name": "Booking Test User",
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "token": token,
        "email": email,
        "user_id": response.json()["id"],
    }