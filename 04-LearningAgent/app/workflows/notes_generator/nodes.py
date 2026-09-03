from langchain_core.language_models import BaseChatModel

from .schemas import LearningContent, Subtopics
from .state import NotesState


def create_subtopics_generator(
    llm: BaseChatModel,
):

    structured_llm = llm.with_structured_output(
        Subtopics
    )

    def generate_subtopics(
        state: NotesState,
    ) -> NotesState:

        topic = state["topic"]

        prompt = f"""
You are an expert technical instructor.

Break the following learning topic into logical
subtopics that should be taught to the learner.

Topic:
{topic["title"]}

Topic description:
{topic["description"]}

Instructions:

1. Start with foundational concepts.
2. Progress logically toward practical concepts.
3. Keep the subtopics focused on the given topic.
4. Do not introduce unrelated subjects.
5. Avoid duplicate or overlapping subtopics.
6. Use clear and concise subtopic names.
7. Generate enough subtopics to teach the topic properly.
"""

        result = structured_llm.invoke(prompt)

        return {
            "subtopics": result.subtopics,
        }

    return generate_subtopics


def create_notes_generator(
    llm: BaseChatModel,
):

    structured_llm = llm.with_structured_output(
        LearningContent
    )

    def generate_notes(
    state: NotesState,
    ) -> NotesState:

        topic = state["topic"]
        subtopics = state["subtopics"]

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
The previous notes generation failed validation.

Validation problems:
{chr(10).join(
    f"- {error}"
    for error in previous_errors
)}

You MUST correct these problems.
"""

        prompt = f"""
You are an expert technical instructor.

Create comprehensive but easy-to-understand learning
notes for the learner based on the topic and its subtopics.

Topic:
{topic["title"]}

Topic description:
{topic["description"]}

Subtopics to cover:
{chr(10).join(f"- {subtopic}" for subtopic in subtopics)}

Instructions:

1. Explain every subtopic clearly.
2. Assume the learner has the existing knowledge described
   in the topic context.
3. Build concepts progressively.
4. Use practical explanations where appropriate.
5. Include useful examples.
6. Avoid unnecessary repetition.
7. Keep the content focused on the given topic.
8. Do not introduce unrelated topics.
9. Make the notes useful for someone preparing to actually
   use this technology.
10. Every generated section must correspond to a meaningful
    subtopic.
    {error_context}
"""

        result = structured_llm.invoke(prompt)

        return {
    "learning_content": result,
    "generation_attempts": generation_attempts,
    "validation_errors": [],
}

    return generate_notes

def validate_notes(
    state: NotesState,
) -> NotesState:

    learning_content = state[
        "learning_content"
    ]

    errors: list[str] = []

    if not learning_content.title.strip():
        errors.append(
            "Learning content title cannot be empty."
        )

    if not learning_content.sections:
        errors.append(
            "Learning content must contain at least one section."
        )

    if not learning_content.key_points:
        errors.append(
            "Learning content must contain at least one key point."
        )

    for section in learning_content.sections:

        if not section.heading.strip():
            errors.append(
                "Every learning section must have a heading."
            )

        if not section.content.strip():
            errors.append(
                f"Section '{section.heading}' "
                "must contain content."
            )

    for point in learning_content.key_points:

        if not point.strip():
            errors.append(
                "Key points cannot contain empty values."
            )

    for example in learning_content.examples:

        if not example.strip():
            errors.append(
                "Examples cannot contain empty values."
            )

    return {
        "validation_errors": errors
    }
MAX_GENERATION_ATTEMPTS = 3


def route_after_notes_validation(
    state: NotesState,
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