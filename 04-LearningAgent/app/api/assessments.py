from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.assessment_service import AssessmentService
from app.schemas.assessment import AssessmentSubmission

router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"],
)


@router.get("/journeys/{journey_id}")
def get_assessment(
    journey_id: int,
    db: Session = Depends(get_db),
):
    service = AssessmentService(db)

    try:
        assessment = service.get_or_generate_assessment(
            journey_id=journey_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "id": assessment.id,
        "journey_id": assessment.journey_id,
        "covered_through_order": assessment.covered_through_order,
        "questions": [
            {
                "id": question.id,
                "question": question.question,
                "options": question.options,
                "topic": question.topic,
                "difficulty": question.difficulty,
                "order": question.order,
            }
            for question in assessment.questions
        ],
    }
@router.post("/{assessment_id}/submit")
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