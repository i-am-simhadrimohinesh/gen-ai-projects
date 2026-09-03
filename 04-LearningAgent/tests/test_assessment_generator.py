from app.db.database import SessionLocal
from app.db.models import Journey
from app.services.learning_service import LearningService
from app.llm.provider import get_llm
from app.workflows.assessment_generator.graph import (
    build_assessment_generator_graph,
)


def main():

    db = SessionLocal()

    try:

        journey = (
            db.query(Journey)
            .order_by(Journey.id)
            .first()
        )

        if journey is None:
            print("No journeys found in the database.")
            print("Create a journey first using POST /journeys.")
            return

        print(f"Testing Journey ID: {journey.id}")
        print(f"Journey: {journey.title}")
        print()

        learning_service = LearningService(db)

        assessment_context = (
            learning_service.get_assessment_context(
                journey.id
            )
        )

        print("Assessment Context")
        print("=" * 60)

        print(
            f"Journey: "
            f"{assessment_context['journey']['title']}"
        )

        print(
            f"Goal: "
            f"{assessment_context['journey']['goal']}"
        )

        print()
        print("Covered Topics:")

        for topic in assessment_context[
            "covered_topics"
        ]:
            print(
                f"  {topic['order']}. "
                f"{topic['title']}"
            )

        print()
        print(
            f"Weak Topics: "
            f"{assessment_context['weak_topics']}"
        )

        print()
        print("Generating assessment...")
        print("=" * 60)

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

        print()
        print("Assessment Result")
        print("=" * 60)

        questions = result.get(
            "questions",
            []
        )

        print(
            f"Number of generated questions: "
            f"{len(questions)}"
        )

        for index, question in enumerate(
            questions,
            start=1,
        ):

            print()
            print(
                f"Question {index}"
            )

            print(
                f"Topic: {question.topic}"
            )

            print(
                f"Difficulty: "
                f"{question.difficulty}"
            )

            print(
                f"Question: "
                f"{question.question}"
            )

            print("Options:")

            for option_index, option in enumerate(
                question.options,
                start=1,
            ):
                print(
                    f"  {option_index}. "
                    f"{option}"
                )

            print(
                f"Correct Answer: "
                f"{question.correct_answer}"
            )

        print()
        print("=" * 60)
        print(
            "Generation Attempts: "
            f"{result.get('generation_attempts', 0)}"
        )

        print(
            "Validation Errors: "
            f"{result.get('validation_errors', [])}"
        )

        if questions and not result.get(
            "validation_errors"
        ):
            print()
            print(
                "Assessment generated and "
                "validated successfully."
            )

    except ValueError as exc:

        print(
            f"Assessment context error: {exc}"
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()
