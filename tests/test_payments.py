from datetime import datetime, timedelta
from uuid import uuid4


CENTRE_TEST_ID = "264da856-f286-4223-8c00-ce62c13c098c"


def auth_headers(user):
    return {
        "Authorization": f"Bearer {user['token']}"
    }


def create_booking(client, user):
    appointment = (
        datetime.utcnow() + timedelta(days=15)
    ).replace(microsecond=0).isoformat()

    response = client.post(
        "/bookings",
        headers=auth_headers(user),
        json={
            "centre_test_id": CENTRE_TEST_ID,
            "appointment_at": appointment,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_successful_payment(client, authenticated_user):
    booking = create_booking(client, authenticated_user)

    response = client.post(
        "/payments",
        headers=auth_headers(authenticated_user),
        json={
            "booking_id": booking["id"],
            "status": "SUCCESS",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["booking_id"] == booking["id"]
    assert data["amount"] == "500.00"
    assert data["status"] == "SUCCESS"
    assert data["transaction_id"] is not None


def test_failed_payment(client, authenticated_user):
    booking = create_booking(client, authenticated_user)

    response = client.post(
        "/payments",
        headers=auth_headers(authenticated_user),
        json={
            "booking_id": booking["id"],
            "status": "FAILED",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["booking_id"] == booking["id"]
    assert data["amount"] == "500.00"
    assert data["status"] == "FAILED"
    assert data["transaction_id"] is None


def test_payment_only_for_pending_booking(
    client,
    authenticated_user,
):
    booking = create_booking(client, authenticated_user)

    first_payment = client.post(
        "/payments",
        headers=auth_headers(authenticated_user),
        json={
            "booking_id": booking["id"],
            "status": "SUCCESS",
        },
    )

    assert first_payment.status_code == 201

    second_payment = client.post(
        "/payments",
        headers=auth_headers(authenticated_user),
        json={
            "booking_id": booking["id"],
            "status": "SUCCESS",
        },
    )

    assert second_payment.status_code == 409


def test_successful_webhook(client):
    email = f"webhook_{uuid4().hex}@example.com"

    signup = client.post(
        "/auth/signup",
        json={
            "name": "Webhook User",
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert signup.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    booking = create_booking(
        client,
        {
            "token": token,
        },
    )

    event_id = f"evt_{uuid4().hex}"
    transaction_id = f"txn_{uuid4().hex}"

    response = client.post(
        "/payments/webhook",
        json={
            "event_id": event_id,
            "booking_id": booking["id"],
            "status": "SUCCESS",
            "amount": 500,
            "transaction_id": transaction_id,
        },
    )

    assert response.status_code == 200, response.json()

    data = response.json()

    assert data["event_id"] == event_id
    assert data["booking_id"] == booking["id"]
    assert data["status"] == "SUCCESS"
    assert data["amount"] == "500.00"
    assert data["transaction_id"] == transaction_id

    booking_response = client.get(
        f"/bookings/{booking['id']}",
        headers=headers,
    )

    assert booking_response.status_code == 200
    assert booking_response.json()["status"] == "CONFIRMED"


def test_duplicate_webhook_is_idempotent(client):
    email = f"idempotency_{uuid4().hex}@example.com"

    signup = client.post(
        "/auth/signup",
        json={
            "name": "Idempotency User",
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert signup.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    booking = create_booking(
        client,
        {
            "token": token,
        },
    )

    event_id = f"evt_{uuid4().hex}"
    transaction_id = f"txn_{uuid4().hex}"

    payload = {
        "event_id": event_id,
        "booking_id": booking["id"],
        "status": "SUCCESS",
        "amount": 500,
        "transaction_id": transaction_id,
    }

    first_response = client.post(
        "/payments/webhook",
        json=payload,
    )

    assert first_response.status_code == 200

    first_payment_id = first_response.json()["id"]

    second_response = client.post(
        "/payments/webhook",
        json=payload,
    )

    assert second_response.status_code == 200

    second_payment_id = second_response.json()["id"]

    assert first_payment_id == second_payment_id


def test_webhook_rejects_wrong_amount(client):
    email = f"amount_{uuid4().hex}@example.com"

    signup = client.post(
        "/auth/signup",
        json={
            "name": "Amount User",
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert signup.status_code == 201

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    booking = create_booking(
        client,
        {
            "token": token,
        },
    )

    response = client.post(
        "/payments/webhook",
        json={
            "event_id": f"evt_{uuid4().hex}",
            "booking_id": booking["id"],
            "status": "SUCCESS",
            "amount": 100,
            "transaction_id": f"txn_{uuid4().hex}",
        },
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == "Payment amount does not match booking amount"
    )