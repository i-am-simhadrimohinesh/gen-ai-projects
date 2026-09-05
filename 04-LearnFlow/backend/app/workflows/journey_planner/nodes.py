from langchain_core.language_models import BaseChatModel

from .schemas import Roadmap
from .state import JourneyPlannerState


MAX_GENERATION_ATTEMPTS = 3


def create_roadmap_generator(llm: BaseChatModel):

    structured_llm = llm.with_structured_output(Roadmap)

    def generate_roadmap(
        state: JourneyPlannerState,
    ) -> JourneyPlannerState:

        journey_input = state["journey_input"]

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
The previous roadmap generation failed validation.

Validation problems:
{chr(10).join(f"- {error}" for error in previous_errors)}

You MUST correct these problems in the new roadmap.
"""

        prompt = f"""
You are an expert learning curriculum designer.

Create a structured learning roadmap based on the learner's
requirements.

Learning subject:
{journey_input.title}

Why the learner wants to learn it:
{journey_input.reason}

Final learning goal:
{journey_input.goal}

Existing knowledge:
{journey_input.existing_knowledge}

Requested topics:
{", ".join(journey_input.requested_topics)
 if journey_input.requested_topics
 else "No specific topics provided"}

Instructions:

1. Create a logical progression from the learner's existing
   knowledge toward the final goal.
2. Start with foundational concepts when necessary.
3. Progress from basic concepts to intermediate concepts.
4. Include practical topics where appropriate.
5. Include at least 3 topics.
6. Keep the roadmap focused on the requested subject.
7. Do not include topics unrelated to the learner's goal.
8. The topic order must start from 1 and increase sequentially.
9. Do not create duplicate topics.
10. Every topic must have a meaningful title and description.

{error_context}
"""

        roadmap = structured_llm.invoke(prompt)

        return {
            "roadmap": roadmap,
            "generation_attempts": generation_attempts,
            "validation_errors": [],
        }

    return generate_roadmap


def validate_roadmap(
    state: JourneyPlannerState,
) -> JourneyPlannerState:

    roadmap = state["roadmap"]

    errors: list[str] = []

    if not roadmap.title.strip():
        errors.append(
            "Roadmap title cannot be empty."
        )

    if not roadmap.goal.strip():
        errors.append(
            "Roadmap goal cannot be empty."
        )

    if len(roadmap.topics) < 3:
        errors.append(
            "Roadmap must contain at least 3 topics."
        )

    orders = [
        topic.order
        for topic in roadmap.topics
    ]

    expected_orders = list(
        range(1, len(orders) + 1)
    )

    if orders != expected_orders:
        errors.append(
            "Topic order must be sequential starting from 1."
        )

    titles = [
        topic.title.strip().lower()
        for topic in roadmap.topics
    ]

    if len(titles) != len(set(titles)):
        errors.append(
            "Roadmap must not contain duplicate topics."
        )

    for topic in roadmap.topics:

        if not topic.title.strip():
            errors.append(
                "Every topic must have a title."
            )

        if not topic.description.strip():
            errors.append(
                f"Topic '{topic.title}' must have a description."
            )

    return {
        "validation_errors": errors
    }


def route_after_validation(
    state: JourneyPlannerState,
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