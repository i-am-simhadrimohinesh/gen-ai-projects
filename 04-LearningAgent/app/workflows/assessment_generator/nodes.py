from langchain_core.language_models import BaseChatModel

from .schemas import Assessment
from .state import AssessmentState


MAX_GENERATION_ATTEMPTS = 2


def create_assessment_generator(
    llm: BaseChatModel,
):

    structured_llm = llm.with_structured_output(
        Assessment
    )

    def generate_assessment(
        state: AssessmentState,
    ) -> AssessmentState:

        assessment_context = state[
            "assessment_context"
        ]

        generation_attempts = (
            state.get("generation_attempts", 0) + 1
        )

        previous_errors = state.get(
            "validation_errors",
            [],
        )

        error_context = ""

        if previous_errors:

            error_context = f"""
The previous assessment generation failed validation.

Validation problems:
{chr(10).join(
    f"- {error}"
    for error in previous_errors
)}

You MUST correct these problems in the new assessment.
"""

        covered_topics = assessment_context[
            "covered_topics"
        ]

        weak_topics = assessment_context.get(
            "weak_topics",
            [],
        )

        covered_topic_text = "\n".join(
            f"- {topic['title']}: "
            f"{topic['description']}"
            for topic in covered_topics
        )

        weak_topic_text = "\n".join(
            f"- {topic['topic']} ({topic['score']:.1f}%)"
            for topic in weak_topics
        )

        if not weak_topic_text:
            weak_topic_text = "No weak topics identified yet."

        prompt = f"""
You are an expert technical assessment designer.

Create a multiple-choice assessment for a learner
based on the topics they have already completed.

Journey:
{assessment_context["journey"]["title"]}

Learning goal:
{assessment_context["journey"]["goal"]}

Completed topics:
{covered_topic_text}

Previously identified weak topics:
{weak_topic_text}

Assessment requirements:

1. Generate exactly 10 questions.
2. Every question must have exactly 4 options.
3. Each question must have exactly one correct answer.
4. The correct answer must exactly match one of the options.
5. Every question must belong to one of the completed topics.
6. Cover the completed topics reasonably across the assessment.
7. If weak topics exist, give them higher question coverage.
8. Do not ask questions about topics that have not been completed.
9. Mix easy, medium, and hard questions where appropriate.
10. Test understanding, not only memorization.
11. Avoid duplicate or nearly identical questions.
12. Keep questions and options clear and unambiguous.
13. Set difficulty to one of:
    - easy
    - medium
    - hard

{error_context}
"""

        result = structured_llm.invoke(prompt)

        # print()
        # print("=" * 60)
        # print("ASSESSMENT GENERATION DEBUG")
        # print("=" * 60)
        # print("Result:", result)
        # print("Number of questions:", len(result.questions))
        # print("=" * 60)

        return {
            "questions": result.questions,
            "generation_attempts": generation_attempts,
            "validation_errors": [],
        }

    return generate_assessment


def validate_assessment(
    state: AssessmentState,
) -> AssessmentState:

    questions = state.get(
        "questions",
        [],
    )
    # print()
    # print("=" * 60)
    # print("ASSESSMENT VALIDATION DEBUG")
    # print("=" * 60)
    # print("Questions received by validator:", len(questions))
    # print("State keys:", list(state.keys()))
    # print("=" * 60)
    errors: list[str] = []

    if len(questions) != 10:

        errors.append(
            f"Assessment must contain exactly 10 questions, "
            f"but {len(questions)} were generated."
        )

    valid_difficulties = {
        "easy",
        "medium",
        "hard",
    }

    covered_topics = {
        topic["title"].strip().lower()
        for topic in state[
            "assessment_context"
        ]["covered_topics"]
    }

    seen_questions: set[str] = set()

    for index, question in enumerate(
        questions,
        start=1,
    ):

        question_text = (
            question.question.strip()
        )

        if not question_text:

            errors.append(
                f"Question {index} cannot be empty."
            )

        normalized_question = (
            question_text.lower()
        )

        if normalized_question in seen_questions:

            errors.append(
                f"Question {index} is a duplicate."
            )

        seen_questions.add(
            normalized_question
        )

        if len(question.options) != 4:

            errors.append(
                f"Question {index} must have exactly 4 options."
            )

        normalized_options = [
            option.strip().lower()
            for option in question.options
        ]

        if len(normalized_options) != len(
            set(normalized_options)
        ):

            errors.append(
                f"Question {index} contains duplicate options."
            )

        if question.correct_answer not in (
            question.options
        ):

            errors.append(
                f"Question {index} has a correct answer "
                "that is not present in its options."
            )

        if (
            question.topic.strip().lower()
            not in covered_topics
        ):

            errors.append(
                f"Question {index} belongs to a topic "
                "that has not been completed."
            )

        if (
            question.difficulty.strip().lower()
            not in valid_difficulties
        ):

            errors.append(
                f"Question {index} has an invalid difficulty."
            )

    return {
        "validation_errors": errors
    }


def route_after_assessment_validation(
    state: AssessmentState,
) -> str:

    errors = state.get(
        "validation_errors",
        [],
    )

    if not errors:
        return "complete"

    generation_attempts = state.get(
        "generation_attempts",
        0,
    )

    if generation_attempts >= MAX_GENERATION_ATTEMPTS:
        return "failed"

    return "retry"