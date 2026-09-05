from typing import TypedDict

from app.schemas.journey import CreateJourneyRequest

from .schemas import Roadmap


class JourneyPlannerState(TypedDict, total=False):

    journey_input: CreateJourneyRequest

    roadmap: Roadmap

    validation_errors: list[str]

    generation_attempts: int