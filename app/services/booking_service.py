from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.centre_test import CentreTest
from app.models.user import User


def create_booking(
    db: Session,
    current_user: User,
    centre_test_id: UUID,
    appointment_at: datetime,
):
    # Validate appointment time
    if appointment_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment time must be in the future",
        )

    # Find centre-test mapping
    centre_test = db.scalar(
        select(CentreTest).where(
            CentreTest.id == centre_test_id
        )
    )

    if not centre_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test is not available at this centre",
        )

    # Create booking
    booking = Booking(
        user_id=current_user.id,
        centre_test_id=centre_test.id,
        appointment_at=appointment_at,
        amount=centre_test.price,
        status=BookingStatus.PENDING,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


def get_user_bookings(
    db: Session,
    current_user: User,
):
    statement = (
        select(Booking)
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
    )

    return list(db.scalars(statement).all())


def get_booking(
    db: Session,
    current_user: User,
    booking_id: UUID,
):
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

    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this booking",
        )

    return booking


def cancel_booking(
    db: Session,
    current_user: User,
    booking_id: UUID,
):
    booking = get_booking(
        db,
        current_user,
        booking_id,
    )

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking is already cancelled",
        )

    if booking.status == BookingStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed booking cannot be cancelled",
        )

    booking.status = BookingStatus.CANCELLED

    db.commit()
    db.refresh(booking)

    return booking