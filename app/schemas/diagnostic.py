from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# -------------------------
# Diagnostic Centre
# -------------------------

class CentreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    location: str = Field(min_length=2, max_length=255)


class CentreResponse(BaseModel):
    id: UUID
    name: str
    location: str

    model_config = ConfigDict(
        from_attributes=True,
    )


# -------------------------
# Diagnostic Test
# -------------------------

class TestCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None


class TestResponse(BaseModel):
    id: UUID
    name: str
    description: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )


# -------------------------
# Centre Test
# -------------------------

class CentreTestCreate(BaseModel):
    test_id: UUID
    price: Decimal = Field(gt=0)


class CentreTestResponse(BaseModel):
    id: UUID
    centre_id: UUID
    test_id: UUID
    price: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )