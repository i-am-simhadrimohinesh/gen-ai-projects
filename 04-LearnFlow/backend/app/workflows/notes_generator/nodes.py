import time

from langchain_core.language_models import BaseChatModel

from .schemas import LearningContent, Subtopics
from .state import NotesState


MAX_SUBTOPICS = 5
MAX_GENERATION_ATTEMPTS = 3
MAX_LLM_RETRIES = 2


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

Create a logical learning sequence of focused subtopics
for the following topic.

Topic: {topic["title"]}
Description: {topic["description"]}

Start from fundamentals and progress toward practical usage.
Keep subtopics focused, non-overlapping, and relevant.
Use concise, clear subtopic names.
"""

        result = structured_llm.invoke(prompt)

        subtopics = result.subtopics[
            :MAX_SUBTOPICS
        ]

        return {
            "subtopics": subtopics,
            "subtopic_contents": [],
        }

    return generate_subtopics


def create_subtopic_notes_generator(
    llm: BaseChatModel,
):

    structured_llm = llm.with_structured_output(
        LearningContent
    )

    def generate_subtopic_notes(
        state: NotesState,
    ) -> NotesState:

        topic = state["topic"]
        subtopic = state["subtopic"]
        subtopic_index = state["subtopic_index"]

        prompt = f"""
You are an expert technical instructor.

Teach this subtopic clearly and practically.

Main topic: {topic["title"]}
Description: {topic["description"]}
Subtopic: {subtopic}

Explain the fundamentals, purpose, working, and practical usage.
Use realistic examples and code when relevant.
Include useful tables, key points, best practices, or common
mistakes when they add value.

Keep the content focused only on this subtopic.

FORMATTING:
- Use valid Markdown.
- Use fenced code blocks with the correct language.
- Put ``` and ``` on separate lines.
- Put each code statement on its own line.
- Use fenced Mermaid blocks for useful diagrams.
- Put each Mermaid statement on its own line.
"""

        result = None

        for attempt in range(
            1,
            MAX_LLM_RETRIES + 1,
        ):
            try:
                result = structured_llm.invoke(
                    prompt
                )
                print(result.sections)
                break

            except Exception:
                if attempt == MAX_LLM_RETRIES:
                    raise

                time.sleep(
                    2 * attempt
                )

        return {
            "subtopic_contents": [
                (
                    subtopic_index,
                    result,
                )
            ]
        }

    return generate_subtopic_notes


def merge_subtopic_notes(
    state: NotesState,
) -> NotesState:

    topic = state["topic"]

    generated_contents = sorted(
        state.get(
            "subtopic_contents",
            [],
        ),
        key=lambda item: item[0],
    )

    sections = []
    key_points = []
    examples = []

    for _, learning_content in generated_contents:

        sections.extend(
            learning_content.sections
        )

        key_points.extend(
            learning_content.key_points
        )

        examples.extend(
            learning_content.examples
        )

    merged_content = LearningContent(
        title=topic["title"],
        sections=sections,
        key_points=key_points,
        examples=examples,
    )

    generation_attempts = (
        state.get("generation_attempts", 0) + 1
    )

    return {
        "learning_content": merged_content,
        "generation_attempts": generation_attempts,
        "validation_errors": [],
    }


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