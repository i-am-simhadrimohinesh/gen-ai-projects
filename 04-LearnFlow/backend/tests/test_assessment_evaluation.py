from app.db.database import SessionLocal
from app.db.models import Journey
from app.services.assessment_service import AssessmentService
from app.schemas.assessment import (
    AssessmentAnswer,
    AssessmentSubmission,
)
from app.workflows.assessment_generator.schemas import (
    Assessment,
    AssessmentQuestion,
)


def test_assessment_evaluation():
    db = SessionLocal()

    try:
        journey = Journey(
            title="Assessment Evaluation Test Journey",
            reason="Testing assessment evaluation",
            goal="Verify assessment scoring",
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

        answers = [
            AssessmentAnswer(
                question_id=question.id,
                selected_answer="Option A",
            )
            for question in saved_assessment.questions
        ]

        submission = AssessmentSubmission(
            answers=answers
        )

        result = service.evaluate_assessment(
            assessment_id=saved_assessment.id,
            submission=submission,
        )

        assert result.assessment_id == saved_assessment.id
        assert result.total_questions == 10
        assert result.answered_questions == 10
        assert result.correct_answers == 10
        assert result.score == 100

        assert len(result.question_results) == 10

        for question_result in result.question_results:
            assert question_result.correct is True
            assert question_result.topic == "Test Topic"

    finally:
        db.close()