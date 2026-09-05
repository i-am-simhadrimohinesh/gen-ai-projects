from app.db.database import SessionLocal
from app.db.models import Journey
from app.services.assessment_service import AssessmentService
from app.workflows.assessment_generator.schemas import (
    Assessment,
    AssessmentQuestion,
)


def test_assessment_persistence():
    db = SessionLocal()

    try:
        journey = Journey(
            title="Assessment Persistence Test Journey",
            reason="Testing assessment persistence",
            goal="Verify assessment questions are saved correctly",
            existing_knowledge="Basic knowledge",
        )

        db.add(journey)
        db.flush()

        assessment = Assessment(
            questions=[
                AssessmentQuestion(
                    question=f"Test question {i}",
                    options=[
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D",
                    ],
                    correct_answer="Option A",
                    topic="Test Topic",
                    difficulty="easy",
                )
                for i in range(1, 11)
            ]
        )

        service = AssessmentService(db)

        saved_assessment = service.save_assessment(
            journey_id=journey.id,
            assessment=assessment,
        )

        assert saved_assessment.id is not None
        assert saved_assessment.journey_id == journey.id
        assert len(saved_assessment.questions) == 10

        for index, question in enumerate(
            saved_assessment.questions,
            start=1,
        ):
            assert question.order == index
            assert question.question == f"Test question {index}"
            assert question.options == [
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ]
            assert question.correct_answer == "Option A"
            assert question.topic == "Test Topic"
            assert question.difficulty == "easy"

    finally:
        db.close()