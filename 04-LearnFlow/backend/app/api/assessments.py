from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.assessment import (
    AssessmentHistoryItem,
    AssessmentResponse,
    AssessmentResult,
    AssessmentSubmission,
)
from app.services.assessment_service import AssessmentService


router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"],
)


@router.get(
    "/journeys/{journey_id}",
    response_model=list[AssessmentHistoryItem],
)
def get_assessment_history(
    journey_id: int,
    db: Session = Depends(get_db),
):
    service = AssessmentService(db)

    try:
        assessments = service.get_assessment_history(
            journey_id=journey_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    history = []

    for assessment in assessments:

        attempts = assessment.attempts

        if attempts:
            best_score = max(
                attempt.score
                for attempt in attempts
            )
            status = "Completed"
            attempt_count = len(attempts)
        else:
            best_score = None
            status = "Not Attempted"
            attempt_count = 0

        history.append(AssessmentHistoryItem(
            id=assessment.id,
            assessment_number=assessment.assessment_number,
            created_at=assessment.created_at,
            status=status,
            best_score=best_score,
            attempts=attempt_count,
        ))

    return history


@router.post(
    "/journeys/{journey_id}",
    response_model=AssessmentResponse,
)
def create_assessment(
    journey_id: int,
    db: Session = Depends(get_db),
):
    service = AssessmentService(db)

    try:
        assessment = service.generate_assessment(
            journey_id=journey_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return assessment


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
):
    service = AssessmentService(db)

    try:
        assessment = service.get_assessment(
            assessment_id=assessment_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return assessment


@router.post("/{assessment_id}/submit",response_model=AssessmentResult,)
def submit_assessment(
    assessment_id: int,
    submission: AssessmentSubmission,
    db: Session = Depends(get_db),
):
    service = AssessmentService(db)

    try:
        result = service.evaluate_assessment(
            assessment_id=assessment_id,
            submission=submission,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return result