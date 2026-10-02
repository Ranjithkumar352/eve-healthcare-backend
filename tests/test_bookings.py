from datetime import datetime, timedelta
from uuid import uuid4


CENTRE_TEST_ID = "264da856-f286-4223-8c00-ce62c13c098c"


def auth_headers(user):
    return {
        "Authorization": f"Bearer {user['token']}"
    }


def future_appointment():
    appointment = datetime.utcnow() + timedelta(days=10)
    return appointment.replace(microsecond=0).isoformat()


def test_create_booking(client, authenticated_user):
    response = client.post(
        "/bookings",
        headers=auth_headers(authenticated_user),
        json={
            "centre_test_id": CENTRE_TEST_ID,
            "appointment_at": future_appointment(),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["user_id"] == authenticated_user["user_id"]
    assert data["centre_test_id"] == CENTRE_TEST_ID
    assert data["amount"] == "500.00"
    assert data["status"] == "PENDING"

    assert "id" in data


def test_list_bookings(client, authenticated_user):
    create_response = client.post(
        "/bookings",
        headers=auth_headers(authenticated_user),
        json={
            "centre_test_id": CENTRE_TEST_ID,
            "appointment_at": future_appointment(),
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/bookings",
        headers=auth_headers(authenticated_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_booking(client, authenticated_user):
    create_response = client.post(
        "/bookings",
        headers=auth_headers(authenticated_user),
        json={
            "centre_test_id": CENTRE_TEST_ID,
            "appointment_at": future_appointment(),
        },
    )

    assert create_response.status_code == 201

    booking_id = create_response.json()["id"]

    response = client.get(
        f"/bookings/{booking_id}",
        headers=auth_headers(authenticated_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == booking_id
    assert data["status"] == "PENDING"


def test_cancel_booking(client, authenticated_user):
    create_response = client.post(
        "/bookings",
        headers=auth_headers(authenticated_user),
        json={
            "centre_test_id": CENTRE_TEST_ID,
            "appointment_at": future_appointment(),
        },
    )

    assert create_response.status_code == 201

    booking_id = create_response.json()["id"]

    response = client.post(
        f"/bookings/{booking_id}/cancel",
        headers=auth_headers(authenticated_user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == booking_id
    assert data["status"] == "CANCELLED"


def test_cancel_booking_twice(client, authenticated_user):
    create_response = client.post(
        "/bookings",
        headers=auth_headers(authenticated_user),
        json={
            "centre_test_id": CENTRE_TEST_ID,
            "appointment_at": future_appointment(),
        },
    )

    assert create_response.status_code == 201

    booking_id = create_response.json()["id"]

    first_cancel = client.post(
        f"/bookings/{booking_id}/cancel",
        headers=auth_headers(authenticated_user),
    )

    assert first_cancel.status_code == 200

    second_cancel = client.post(
        f"/bookings/{booking_id}/cancel",
        headers=auth_headers(authenticated_user),
    )

    assert second_cancel.status_code == 409

    assert (
        second_cancel.json()["detail"]
        == "Booking is already cancelled"
    )


def test_create_booking_without_authentication(client):
    response = client.post(
        "/bookings",
        json={
            "centre_test_id": CENTRE_TEST_ID,
            "appointment_at": future_appointment(),
        },
    )

    assert response.status_code == 401