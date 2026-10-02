from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User


def create_payment(
    db: Session,
    current_user: User,
    booking_id: UUID,
    payment_status: PaymentStatus,
):
    # 1. Find booking
    booking = db.scalar(
        select(Booking).where(
            Booking.id == booking_id
        )
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # 2. Verify booking ownership
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to make payment for this booking",
        )

    # 3. Payment is allowed only for PENDING bookings
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment can only be made for a pending booking",
        )

    # 4. Generate event ID
    event_id = str(uuid4())

    # 5. Generate transaction ID only for successful payments
    transaction_id = (
        str(uuid4())
        if payment_status == PaymentStatus.SUCCESS
        else None
    )

    # 6. Create payment
    payment = Payment(
        booking_id=booking.id,
        event_id=event_id,
        amount=booking.amount,
        status=payment_status,
        transaction_id=transaction_id,
    )

    # 7. Update booking status
    if payment_status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED

    db.add(payment)

    db.commit()
    db.refresh(payment)

    return payment


def process_payment_webhook(
    db: Session,
    event_id: str,
    booking_id: UUID,
    payment_status: PaymentStatus,
    amount: Decimal,
    transaction_id: str | None = None,
):
    # 1. Check whether this event was already processed
    existing_payment = db.scalar(
        select(Payment).where(
            Payment.event_id == event_id
        )
    )

    if existing_payment:
        # Same event must have the same payload
        if (
            existing_payment.booking_id != booking_id
            or existing_payment.status != payment_status
            or existing_payment.amount != amount
            or existing_payment.transaction_id != transaction_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Event ID already exists with different payment data",
            )

        # Idempotent response
        return existing_payment

    # 2. Find booking
    booking = db.scalar(
        select(Booking).where(
            Booking.id == booking_id
        )
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # 3. Verify payment amount
    if booking.amount != amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount does not match booking amount",
        )

    # 4. Booking must still be pending
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking is no longer pending",
        )

    # 5. Create payment
    payment = Payment(
        booking_id=booking.id,
        event_id=event_id,
        amount=amount,
        status=payment_status,
        transaction_id=transaction_id,
    )

    # 6. Update booking
    if payment_status == PaymentStatus.SUCCESS:
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED

    db.add(payment)

    try:
        db.commit()
        db.refresh(payment)

    except IntegrityError:
        # Handles concurrent duplicate webhook requests
        db.rollback()

        existing_payment = db.scalar(
            select(Payment).where(
                Payment.event_id == event_id
            )
        )

        if existing_payment:
            return existing_payment

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment event could not be processed",
        )

    return payment