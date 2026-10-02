from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.schemas.diagnostic import (
    CentreCreate,
    CentreResponse,
    CentreTestCreate,
    CentreTestResponse,
    TestCreate,
    TestResponse,
)
from app.services.diagnostic_service import (
    add_test_to_centre,
    create_centre,
    create_test,
    get_centre,
    get_centre_tests,
    get_centres,
    get_test,
    get_tests,
)


router = APIRouter(
    tags=["Diagnostics"],
)


# =====================================================
# Diagnostic Centres
# =====================================================

@router.post(
    "/diagnostic-centres",
    response_model=CentreResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_diagnostic_centre(
    data: CentreCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_centre(
        db=db,
        name=data.name,
        location=data.location,
    )


@router.get(
    "/diagnostic-centres",
    response_model=list[CentreResponse],
)
def list_diagnostic_centres(
    db: Session = Depends(get_db),
):
    return get_centres(db)


@router.get(
    "/diagnostic-centres/{centre_id}",
    response_model=CentreResponse,
)
def get_diagnostic_centre(
    centre_id: UUID,
    db: Session = Depends(get_db),
):
    centre = get_centre(
        db,
        centre_id,
    )

    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    return centre


# =====================================================
# Diagnostic Tests
# =====================================================

@router.post(
    "/tests",
    response_model=TestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_diagnostic_test(
    data: TestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_test(
        db=db,
        name=data.name,
        description=data.description,
    )


@router.get(
    "/tests",
    response_model=list[TestResponse],
)
def list_diagnostic_tests(
    db: Session = Depends(get_db),
):
    return get_tests(db)


@router.get(
    "/tests/{test_id}",
    response_model=TestResponse,
)
def get_diagnostic_test(
    test_id: UUID,
    db: Session = Depends(get_db),
):
    diagnostic_test = get_test(
        db,
        test_id,
    )

    if not diagnostic_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )

    return diagnostic_test


# =====================================================
# Centre ↔ Test
# =====================================================

@router.post(
    "/diagnostic-centres/{centre_id}/tests",
    response_model=CentreTestResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_test_to_diagnostic_centre(
    centre_id: UUID,
    data: CentreTestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    centre = get_centre(
        db,
        centre_id,
    )

    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    diagnostic_test = get_test(
        db,
        data.test_id,
    )

    if not diagnostic_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic test not found",
        )

    return add_test_to_centre(
        db=db,
        centre_id=centre_id,
        test_id=data.test_id,
        price=data.price,
    )


@router.get(
    "/diagnostic-centres/{centre_id}/tests",
    response_model=list[CentreTestResponse],
)
def list_centre_tests(
    centre_id: UUID,
    db: Session = Depends(get_db),
):
    centre = get_centre(
        db,
        centre_id,
    )

    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic centre not found",
        )

    return get_centre_tests(
        db,
        centre_id,
    )