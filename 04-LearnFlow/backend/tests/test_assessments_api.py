from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.db.models import (
    Journey,
    Assessment,
    AssessmentAttempt,
    LearnerKnowledge,
)
from app.services.assessment_service import AssessmentService
from app.workflows.assessment_generator.schemas import (
    Assessment as AssessmentSchema,
    AssessmentQuestion,
)


client = TestClient(app)


def test_get_assessment_history():
    db = SessionLocal()

    try:
        journey = Journey(
            title="API Assessment History Test",
            reason="Testing assessment history endpoint",
            goal="Verify assessment history response",
            existing_knowledge="Basic knowledge",
        )

        db.add(journey)
        db.flush()

        assessment = Assessment(
            journey_id=journey.id,
            assessment_number=1,
        )

        db.add(assessment)
        db.flush()

        attempt = AssessmentAttempt(
            assessment_id=assessment.id,
            score=80,
            total_questions=10,
            answered_questions=10,
            correct_answers=8,
        )

        db.add(attempt)
        db.commit()

        response = client.get(
            f"/assessments/journeys/{journey.id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1

        history_item = data[0]

        assert history_item["id"] == assessment.id
        assert history_item["status"] == "Completed"
        assert history_item["best_score"] == 80
        assert history_item["attempts"] == 1

    finally:
        db.close()


def test_create_assessment():
    db = SessionLocal()

    try:
        journey = Journey(
            title="API Create Assessment Test",
            reason="Testing assessment creation endpoint",
            goal="Verify new assessment creation",
            existing_knowledge="Basic knowledge",
        )

        db.add(journey)
        db.commit()

        assessment = AssessmentSchema(
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
                    topic="Completed Test Topic",
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

        with patch.object(
            AssessmentService,
            "generate_assessment",
            return_value=saved_assessment,
        ):
            response = client.post(
                f"/assessments/journeys/{journey.id}"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == saved_assessment.id
        assert data["journey_id"] == journey.id
        assert data["created_at"] is not None

        assert len(data["questions"]) == 10
        assert data["attempts"] == []

        for index, question in enumerate(
            data["questions"],
            start=1,
        ):
            assert question["id"] is not None

            assert question["question"] == (
                f"Test question {index}"
            )

            assert len(question["options"]) == 4

            assert question["topic"] == (
                "Completed Test Topic"
            )

            assert question["difficulty"] == "easy"
            assert question["order"] == index

            # Correct answers must never be exposed
            # through the assessment API response.
            assert "correct_answer" not in question

    finally:
        db.close()


def test_get_assessment():
    db = SessionLocal()

    try:
        journey = Journey(
            title="API Get Assessment Test",
            reason="Testing get assessment endpoint",
            goal="Verify assessment retrieval",
            existing_knowledge="Basic knowledge",
        )

        db.add(journey)
        db.flush()

        assessment = AssessmentSchema(
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
                    topic="Completed Test Topic",
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

        response = client.get(
            f"/assessments/{saved_assessment.id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == saved_assessment.id
        assert data["journey_id"] == journey.id
        assert data["created_at"] is not None

        assert len(data["questions"]) == 10

        assert data["attempts"] == []

        for index, question in enumerate(
            data["questions"],
            start=1,
        ):
            assert question["id"] is not None

            assert question["question"] == (
                f"Test question {index}"
            )

            assert question["options"] == [
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ]

            assert question["topic"] == (
                "Completed Test Topic"
            )

            assert question["difficulty"] == "easy"
            assert question["order"] == index

            # Correct answers must never be exposed
            # through the assessment API response.
            assert "correct_answer" not in question

    finally:
        db.close()
def test_submit_assessment():
    db = SessionLocal()

    try:
        journey = Journey(
            title="API Submit Assessment Test",
            reason="Testing assessment submission endpoint",
            goal="Verify assessment submission and result",
            existing_knowledge="Basic knowledge",
        )

        db.add(journey)
        db.flush()

        assessment = AssessmentSchema(
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
                    topic="Completed Test Topic",
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
            {
                "question_id": question.id,
                "selected_answer": (
                    "Option A"
                    if index <= 7
                    else "Option B"
                ),
            }
            for index, question in enumerate(
                saved_assessment.questions,
                start=1,
            )
        ]

        response = client.post(
            f"/assessments/{saved_assessment.id}/submit",
            json={
                "answers": answers,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["assessment_id"] == (
            saved_assessment.id
        )

        assert data["total_questions"] == 10
        assert data["answered_questions"] == 10
        assert data["correct_answers"] == 7
        assert data["score"] == 70

        assert len(data["question_results"]) == 10

        for index, result in enumerate(
            data["question_results"],
            start=1,
        ):
            assert result["question_id"] is not None
            assert result["topic"] == "Completed Test Topic"

            if index <= 7:
                assert result["correct"] is True
            else:
                assert result["correct"] is False

        # Verify the attempt was persisted.
        db.expire_all()

        attempt = (
            db.query(AssessmentAttempt)
            .filter(
                AssessmentAttempt.assessment_id
                == saved_assessment.id
            )
            .first()
        )

        assert attempt is not None
        assert attempt.score == 70
        assert attempt.total_questions == 10
        assert attempt.answered_questions == 10
        assert attempt.correct_answers == 7

        # Verify learner knowledge was updated.
        knowledge = (
            db.query(LearnerKnowledge)
            .filter(
                LearnerKnowledge.journey_id
                == journey.id,
                LearnerKnowledge.topic
                == "Completed Test Topic",
            )
            .first()
        )

        assert knowledge is not None
        assert knowledge.attempts == 1
        assert knowledge.best_score == 70

    finally:
        db.close()