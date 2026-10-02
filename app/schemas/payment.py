from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    booking_id: UUID
    status: PaymentStatus


class PaymentResponse(BaseModel):
    id: UUID
    booking_id: UUID
    event_id: str
    amount: Decimal
    status: PaymentStatus
    transaction_id: str | None

    model_config = ConfigDict(from_attributes=True)


class PaymentWebhookRequest(BaseModel):
    event_id: str = Field(min_length=1, max_length=255)
    booking_id: UUID
    status: PaymentStatus
    amount: Decimal = Field(gt=0)
    transaction_id: str | None = None