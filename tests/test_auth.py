from uuid import uuid4


def unique_email(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}@example.com"


def test_signup(client):
    email = unique_email("testuser")

    response = client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test User"
    assert data["email"] == email
    assert "id" in data


def test_duplicate_signup(client):
    email = unique_email("duplicate")

    payload = {
        "name": "Duplicate User",
        "email": email,
        "password": "TestPassword123!",
    }

    first_response = client.post(
        "/auth/signup",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/signup",
        json=payload,
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"


def test_login(client):
    email = unique_email("login")
    password = "TestPassword123!"

    signup_response = client.post(
        "/auth/signup",
        json={
            "name": "Login User",
            "email": email,
            "password": password,
        },
    )

    assert signup_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == email


def test_login_invalid_password(client):
    email = unique_email("invalid_password")

    signup_response = client.post(
        "/auth/signup",
        json={
            "name": "Invalid Password User",
            "email": email,
            "password": "CorrectPassword123!",
        },
    )

    assert signup_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123!",
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Invalid email or password"


def test_auth_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401