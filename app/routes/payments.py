from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentWebhookRequest,
)
from app.services.payment_service import (
    create_payment,
    process_payment_webhook,
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


# --------------------------------------------------
# Create Payment
# --------------------------------------------------

@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def make_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_payment(
        db=db,
        current_user=current_user,
        booking_id=data.booking_id,
        payment_status=data.status,
    )


# --------------------------------------------------
# Payment Webhook
# --------------------------------------------------

@router.post(
    "/webhook",
    response_model=PaymentResponse,
)
def payment_webhook(
    data: PaymentWebhookRequest,
    db: Session = Depends(get_db),
):
    return process_payment_webhook(
        db=db,
        event_id=data.event_id,
        booking_id=data.booking_id,
        payment_status=data.status,
        amount=data.amount,
        transaction_id=data.transaction_id,
    )