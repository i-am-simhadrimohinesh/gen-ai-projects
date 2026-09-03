from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.learning_service import LearningService
from fastapi.responses import Response


router = APIRouter(
    prefix="/topics",
    tags=["Topics"],
)


@router.get("/{topic_id}/notes")
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

@router.get("/{topic_id}/notes/download")
def download_topic_notes(
    topic_id: int,
    db: Session = Depends(get_db),
):

    try:

        service = LearningService(db)

        markdown, filename = (
            service.get_topic_notes_markdown(
                topic_id
            )
        )

        return Response(
            content=markdown,
            media_type="text/markdown",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{filename}"'
                )
            },
        )

    except ValueError as exc:

        message = str(exc)

        status_code = (
            404
            if message == "Topic not found."
            else 422
        )

        raise HTTPException(
            status_code=status_code,
            detail=message,
        )
@router.post("/{topic_id}/complete")
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