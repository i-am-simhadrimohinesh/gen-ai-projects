from app.db.database import SessionLocal
from app.db.models import (
    Journey,
    LearnerKnowledge,
    Topic,
)
from app.services.learning_service import LearningService


def test_get_assessment_context():
    db = SessionLocal()

    try:
        journey = Journey(
            title="Assessment Context Test Journey",
            reason="Testing assessment context",
            goal="Verify assessment context generation",
            existing_knowledge="Basic knowledge",
        )

        db.add(journey)
        db.flush()

        completed_topic = Topic(
            journey_id=journey.id,
            title="Completed Topic",
            description="A completed learning topic",
            order=1,
            completed=True,
        )

        pending_topic = Topic(
            journey_id=journey.id,
            title="Pending Topic",
            description="A pending learning topic",
            order=2,
            completed=False,
        )

        db.add_all([
            completed_topic,
            pending_topic,
        ])

        weak_topic = LearnerKnowledge(
            journey_id=journey.id,
            topic="Completed Topic",
            attempts=2,
            best_score=50,
        )

        strong_topic = LearnerKnowledge(
            journey_id=journey.id,
            topic="Another Topic",
            attempts=3,
            best_score=80,
        )

        db.add_all([
            weak_topic,
            strong_topic,
        ])

        db.commit()

        service = LearningService(db)

        context = service.get_assessment_context(
            journey.id
        )

        assert context["journey"]["title"] == (
            "Assessment Context Test Journey"
        )

        assert len(context["covered_topics"]) == 1

        covered_topic = context["covered_topics"][0]

        assert covered_topic["title"] == "Completed Topic"
        assert covered_topic["order"] == 1

        covered_topic_names = [
            topic["title"]
            for topic in context["covered_topics"]
        ]

        assert "Pending Topic" not in covered_topic_names

        weak_topics = context["weak_topics"]

        weak_topic_names = [
            topic["topic"]
            for topic in weak_topics
        ]

        assert "Completed Topic" in weak_topic_names
        assert "Another Topic" not in weak_topic_names

        weak_topic_result = next(
            topic
            for topic in weak_topics
            if topic["topic"] == "Completed Topic"
        )

        assert weak_topic_result["score"] == 50

    finally:
        db.close()