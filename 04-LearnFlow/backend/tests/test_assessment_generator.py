from app.db.database import SessionLocal
from app.db.models import Journey, Topic
from app.services.learning_service import LearningService
from app.llm.provider import get_llm
from app.workflows.assessment_generator.graph import (
    build_assessment_generator_graph,
)


def test_assessment_generator_creates_valid_assessment():
    db = SessionLocal()

    try:
        journey = Journey(
            title="Assessment Generator Test Journey",
            reason="Testing assessment generation",
            goal="Verify assessment generator creates valid questions",
            existing_knowledge="Basic knowledge",
        )

        db.add(journey)
        db.flush()

        topic = Topic(
            journey_id=journey.id,
            title="Assessment Generator Test Topic",
            description="A completed topic used for assessment generation testing.",
            order=1,
            completed=True,
        )

        db.add(topic)
        db.commit()

        learning_service = LearningService(db)

        assessment_context = (
            learning_service.get_assessment_context(
                journey.id
            )
        )

        assert assessment_context["journey"]
        assert "covered_topics" in assessment_context
        assert "weak_topics" in assessment_context

        llm = get_llm()

        assessment_generator = (
            build_assessment_generator_graph(llm)
        )

        initial_state = {
            "journey_id": journey.id,
            "journey": assessment_context["journey"],
            "covered_topics": assessment_context[
                "covered_topics"
            ],
            "weak_topics": assessment_context[
                "weak_topics"
            ],
            "assessment_context": assessment_context,
            "generation_attempts": 0,
            "validation_errors": [],
        }

        result = assessment_generator.invoke(
            initial_state
        )

        questions = result.get(
            "questions",
            []
        )

        assert questions
        assert len(questions) == 10

        assert result.get(
            "validation_errors",
            []
        ) == []

        assert result.get(
            "generation_attempts",
            0
        ) >= 1

        for index, question in enumerate(
            questions,
            start=1,
        ):
            assert question.question
            assert question.options
            assert len(question.options) == 4
            assert question.correct_answer
            assert question.correct_answer in question.options
            assert question.topic
            assert question.difficulty

    finally:
        db.close()