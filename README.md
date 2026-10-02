# EVE Healthcare - Backend Engineering Assignment

A backend service for managing diagnostic test bookings and simulated payments, built as part of the EVE Healthcare SDE Intern Backend Engineering Assignment.

The application provides APIs for:

- User signup and login
- JWT-based authentication
- Diagnostic centres and tests
- Test availability and pricing
- Diagnostic test bookings
- Simulated payments
- Payment webhooks
- Idempotent webhook processing
- Booking status management
- Request validation and authorization

---

## 1. Tech Stack

### Backend

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Pydantic
- Pydantic Settings
- PyJWT
- pwdlib
- Argon2

### Database

- PostgreSQL
- psycopg2

### Testing

- pytest
- FastAPI TestClient
- HTTPX

### Development Tools

- Git
- GitHub
- Swagger / OpenAPI

---

## 2. Project Structure

```text
eve-healthcare-backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── base.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── diagnostic_centre.py
│   │   ├── diagnostic_test.py
│   │   ├── centre_test.py
│   │   ├── booking.py
│   │   └── payment.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── diagnostic.py
│   │   ├── booking.py
│   │   └── payment.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── diagnostics.py
│   │   ├── bookings.py
│   │   └── payments.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── auth_service.py
│       ├── diagnostic_service.py
│       ├── booking_service.py
│       └── payment_service.py
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_bookings.py
│   └── test_payments.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── Dockerfile