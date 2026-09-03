from typing import TypedDict

from .schemas import CreateJourneyRequest, Roadmap


class JourneyPlannerState(TypedDict, total=False):

    journey_input: CreateJourneyRequest

    roadmap: Roadmap

    validation_errors: list[str]

    generation_attempts: int