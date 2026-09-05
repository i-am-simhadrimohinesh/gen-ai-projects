from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.learning_service import LearningService
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from app.schemas.topic import (
    TopicNotesResponse,
    TopicCompletionResponse,
)

router = APIRouter(
    prefix="/topics",
    tags=["Topics"],
)


@router.get("/{topic_id}/notes",response_model=TopicNotesResponse,)
def get_topic_notes(
    topic_id: int,
    db: Session = Depends(get_db),
):

    try:

        service = LearningService(db)

        learning_content = (
            service.get_topic_notes(
                topic_id
            )
        )

        return {
            "id": learning_content.id,
            "topic_id": learning_content.topic_id,
            "content": learning_content.content,
        }

    except ValueError as exc:

        status_code = (
            404
            if str(exc) == "Topic not found."
            else 422
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        )
@router.post("/{topic_id}/complete",response_model=TopicCompletionResponse,)
def complete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
):

    try:

        service = LearningService(db)

        topic = service.complete_topic(
            topic_id
        )

        return {
            "id": topic.id,
            "title": topic.title,
            "completed": topic.completed,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )