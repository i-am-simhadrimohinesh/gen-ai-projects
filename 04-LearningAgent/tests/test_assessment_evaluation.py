from app.db.database import SessionLocal
from app.db.models import Assessment
from app.services.assessment_service import AssessmentService
from app.schemas.assessment import (
    AssessmentAnswer,
    AssessmentSubmission,
)


def main():
    db = SessionLocal()

    try:
        assessment_id = 1  # Change if needed

        assessment = (
            db.query(Assessment)
            .filter(Assessment.id == assessment_id)
            .first()
        )

        if assessment is None:
            print("Assessment not found.")
            return

        print()
        print("=" * 60)
        print("ASSESSMENT EVALUATION TEST")
        print("=" * 60)
        print("Assessment ID:", assessment.id)
        print("Questions:", len(assessment.questions))

        # --------------------------------------------------
        # Build test submission
        #
        # For testing, select the first option for every
        # question.
        # --------------------------------------------------

        answers = []

        for question in assessment.questions:
            answers.append(
                AssessmentAnswer(
                    question_id=question.id,
                    selected_answer=question.options[0],
                )
            )

        submission = AssessmentSubmission(
            answers=answers
        )

        # --------------------------------------------------
        # Evaluate
        # --------------------------------------------------

        service = AssessmentService(db)

        result = service.evaluate_assessment(
            assessment_id=assessment.id,
            submission=submission,
        )

        print()
        print("-" * 60)
        print("RESULT")
        print("-" * 60)

        print("Assessment ID:", result.assessment_id)
        print("Total questions:", result.total_questions)
        print("Answered questions:", result.answered_questions)
        print("Correct answers:", result.correct_answers)
        print("Score:", result.score)

        print()
        print("-" * 60)
        print("QUESTION RESULTS")
        print("-" * 60)

        for question_result in result.question_results:
            print(
                f"Question ID: {question_result.question_id} | "
                f"Topic: {question_result.topic} | "
                f"Correct: {question_result.correct}"
            )

        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()