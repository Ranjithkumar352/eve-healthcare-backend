from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CentreTest(Base):
    __tablename__ = "centre_tests"

    __table_args__ = (
        UniqueConstraint(
            "centre_id",
            "test_id",
            name="uq_centre_test",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    centre_id: Mapped[UUID] = mapped_column(
        ForeignKey("diagnostic_centres.id"),
        nullable=False,
    )

    test_id: Mapped[UUID] = mapped_column(
        ForeignKey("diagnostic_tests.id"),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    centre = relationship(
        "DiagnosticCentre",
        back_populates="centre_tests",
    )

    test = relationship(
        "DiagnosticTest",
        back_populates="centre_tests",
    )
    
    bookings = relationship(
        "Booking",
        back_populates="centre_test",
    )