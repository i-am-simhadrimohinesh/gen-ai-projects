from app.db.database import SessionLocal
from app.services.assessment_service import AssessmentService


def main():
    db = SessionLocal()

    try:
        journey_id = 1  # Change if needed

        service = AssessmentService(db)

        # assessment = service.generate_assessment(
        #     journey_id=journey_id
        # )
        assessment = service.get_or_generate_assessment(
            journey_id=journey_id
        )

        print()
        print("=" * 60)
        print("ASSESSMENT SERVICE TEST")
        print("=" * 60)
        print("Assessment ID:", assessment.id)
        print("Journey ID:", assessment.journey_id)
        print("Questions:", len(assessment.questions))
        print("=" * 60)

        for question in assessment.questions:
            print()
            print(f"{question.order}. {question.question}")
            print("Topic:", question.topic)
            print("Difficulty:", question.difficulty)
            print("Options:", question.options)

    finally:
        db.close()


if __name__ == "__main__":
    main()