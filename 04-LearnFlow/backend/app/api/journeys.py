from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.journey_service import JourneyService
from app.schemas.journey import (
    CreateJourneyRequest,
    JourneyResponse,
    JourneySummaryResponse,
)


router = APIRouter(
    prefix="/journeys",
    tags=["Journeys"],
)


@router.post("",response_model=JourneyResponse)
def create_journey(
    journey_input: CreateJourneyRequest,
    db: Session = Depends(get_db),
):

    try:

        service = JourneyService(db)

        journey = service.create_journey(
            journey_input
        )

        return {
            "id": journey.id,
            "title": journey.title,
            "reason": journey.reason,
            "goal": journey.goal,
            "existing_knowledge": (
                journey.existing_knowledge
            ),
            "topics": [
                {
                    "id": topic.id,
                    "title": topic.title,
                    "description": topic.description,
                    "order": topic.order,
                    "completed": topic.completed,
                }
                for topic in journey.topics
            ],
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )
    
@router.get("",response_model=list[JourneySummaryResponse],)
def get_journeys(
    db: Session = Depends(get_db),
):

    service = JourneyService(db)

    journeys = service.get_journeys()

    return [
        {
            "id": journey.id,
            "title": journey.title,
            "goal": journey.goal,
        }
        for journey in journeys
    ]
@router.delete("/{journey_id}")
def delete_journey(
    journey_id: int,
    db: Session = Depends(get_db),
):
    service = JourneyService(db)

    try:
        service.delete_journey(
            journey_id=journey_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "message": "Journey deleted successfully."
    }
@router.get("/{journey_id}",response_model=JourneyResponse,)
def get_journey(
    journey_id: int,
    db: Session = Depends(get_db),
):

    service = JourneyService(db)

    journey = service.get_journey(
        journey_id
    )

    if journey is None:
        raise HTTPException(
            status_code=404,
            detail="Journey not found.",
        )

    return {
        "id": journey.id,
        "title": journey.title,
        "reason": journey.reason,
        "goal": journey.goal,
        "existing_knowledge": (
            journey.existing_knowledge
        ),
        "topics": [
            {
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "order": topic.order,
                "completed": topic.completed,
            }
            for topic in journey.topics
        ],
    }