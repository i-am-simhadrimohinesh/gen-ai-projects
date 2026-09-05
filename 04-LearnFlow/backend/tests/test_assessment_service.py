from app.db.database import SessionLocal
from app.db.models import Journey, LearnerKnowledge
from app.services.learning_service import LearningService


def test_get_weak_topics_uses_best_score():
    db = SessionLocal()

    try:
        journey = Journey(
            title="Weak Topic Test Journey",
            reason="Testing weak topic detection",
            goal="Verify best score threshold",
            existing_knowledge="Basic knowledge",
        )

        db.add(journey)
        db.flush()

        weak_topic = LearnerKnowledge(
            journey_id=journey.id,
            topic="Weak Topic",
            attempts=2,
            best_score=50,
        )

        strong_topic = LearnerKnowledge(
            journey_id=journey.id,
            topic="Strong Topic",
            attempts=3,
            best_score=75,
        )

        db.add_all([
            weak_topic,
            strong_topic,
        ])

        db.commit()

        service = LearningService(db)

        weak_topics = service.get_weak_topics(
            journey_id=journey.id
        )

        weak_topic_names = [
            item["topic"]
            for item in weak_topics
        ]

        assert "Weak Topic" in weak_topic_names
        assert "Strong Topic" not in weak_topic_names

        weak_topic_result = next(
            item
            for item in weak_topics
            if item["topic"] == "Weak Topic"
        )

        assert weak_topic_result["score"] == 50

    finally:
        db.close()