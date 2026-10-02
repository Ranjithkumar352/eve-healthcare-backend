from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.centre_test import CentreTest
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.diagnostic_test import DiagnosticTest


# -------------------------
# Diagnostic Centres
# -------------------------

def create_centre(
    db: Session,
    name: str,
    location: str,
) -> DiagnosticCentre:

    centre = DiagnosticCentre(
        name=name,
        location=location,
    )

    db.add(centre)
    db.commit()
    db.refresh(centre)

    return centre


def get_centres(
    db: Session,
) -> list[DiagnosticCentre]:

    statement = select(DiagnosticCentre).order_by(
        DiagnosticCentre.name
    )

    return list(db.scalars(statement).all())


def get_centre(
    db: Session,
    centre_id: UUID,
) -> DiagnosticCentre | None:

    return db.get(
        DiagnosticCentre,
        centre_id,
    )


# -------------------------
# Diagnostic Tests
# -------------------------

def create_test(
    db: Session,
    name: str,
    description: str | None,
) -> DiagnosticTest:

    diagnostic_test = DiagnosticTest(
        name=name,
        description=description,
    )

    db.add(diagnostic_test)
    db.commit()
    db.refresh(diagnostic_test)

    return diagnostic_test


def get_tests(
    db: Session,
) -> list[DiagnosticTest]:

    statement = select(DiagnosticTest).order_by(
        DiagnosticTest.name
    )

    return list(db.scalars(statement).all())


def get_test(
    db: Session,
    test_id: UUID,
) -> DiagnosticTest | None:

    return db.get(
        DiagnosticTest,
        test_id,
    )


# -------------------------
# Centre ↔ Test
# -------------------------

def add_test_to_centre(
    db: Session,
    centre_id: UUID,
    test_id: UUID,
    price,
):
    # Check centre exists
    centre = db.scalar(
        select(DiagnosticCentre).where(DiagnosticCentre.id == centre_id)
    )

    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    # Check test exists
    test = db.scalar(
        select(DiagnosticTest).where(DiagnosticTest.id == test_id)
    )

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )

    # Check duplicate assignment
    existing = db.scalar(
        select(CentreTest).where(
            CentreTest.centre_id == centre_id,
            CentreTest.test_id == test_id,
        )
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test is already available at this centre",
        )

    centre_test = CentreTest(
        centre_id=centre_id,
        test_id=test_id,
        price=price,
    )

    db.add(centre_test)

    try:
        db.commit()
        db.refresh(centre_test)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Test is already available at this centre",
        )

    return centre_test


def get_centre_tests(
    db: Session,
    centre_id: UUID,
) -> list[CentreTest]:

    statement = (
        select(CentreTest)
        .where(CentreTest.centre_id == centre_id)
    )

    return list(db.scalars(statement).all())