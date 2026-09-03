from typing import TypedDict

from .schemas import AssessmentQuestion


class AssessmentState(TypedDict, total=False):
    journey_id: int
    journey: dict
    covered_topics: list[dict]
    weak_topics: list[dict]
    assessment_context: dict

    questions: list[AssessmentQuestion]

    validation_errors: list[str]
    generation_attempts: int