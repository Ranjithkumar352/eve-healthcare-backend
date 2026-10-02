from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import (
    create_booking,
    get_user_bookings,
    get_booking,
    cancel_booking,
)


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking_endpoint(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_booking(
        db=db,
        current_user=current_user,
        centre_test_id=data.centre_test_id,
        appointment_at=data.appointment_at,
    )


@router.get(
    "",
    response_model=list[BookingResponse],
)
def list_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_bookings(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking_endpoint(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_booking(
        db=db,
        current_user=current_user,
        booking_id=booking_id,
    )


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
)
def cancel_booking_endpoint(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cancel_booking(
        db=db,
        current_user=current_user,
        booking_id=booking_id,
    )