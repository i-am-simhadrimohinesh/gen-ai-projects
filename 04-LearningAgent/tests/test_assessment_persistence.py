from app.db.database import SessionLocal
from app.services.assessment_service import AssessmentService
from app.workflows.assessment_generator.schemas import (
    Assessment,
    AssessmentQuestion,
)


def main():
    db = SessionLocal()

    try:
        journey_id = 1  # Change if your existing journey has a different ID

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
            journey_id=journey_id,
            assessment=assessment,
        )

        print()
        print("=" * 60)
        print("ASSESSMENT PERSISTENCE TEST")
        print("=" * 60)
        print("Assessment ID:", saved_assessment.id)
        print("Journey ID:", saved_assessment.journey_id)
        print("Questions saved:", len(saved_assessment.questions))
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()