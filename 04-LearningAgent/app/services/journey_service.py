from sqlalchemy.orm import Session

from app.llm.provider import get_llm
from app.workflows.journey_planner.graph import (
    build_journey_planner_graph,
)
from app.workflows.journey_planner.schemas import (
    CreateJourneyRequest,
    Roadmap,
)

from app.db.models import Journey, Topic


class JourneyService:

    def __init__(self, db: Session):
        self.db = db

        self.llm = get_llm()

        self.journey_planner = (
            build_journey_planner_graph(self.llm)
        )

    def get_journeys(self) -> list[Journey]:

        return (
            self.db.query(Journey)
            .order_by(Journey.created_at.desc())
            .all()
        )
    def get_journey(
    self,
    journey_id: int,
    ) -> Journey | None:

        return (
            self.db.query(Journey)
            .filter(Journey.id == journey_id)
            .first()
        )
    def create_journey(
        self,
        journey_input: CreateJourneyRequest,
    ) -> Journey:

        initial_state = {
            "journey_input": journey_input,
            "generation_attempts": 0,
            "validation_errors": [],
        }

        result = self.journey_planner.invoke(
            initial_state
        )

        validation_errors = result.get(
            "validation_errors",
            [],
        )

        if validation_errors:
            raise ValueError(
                "Unable to generate a valid roadmap: "
                + "; ".join(validation_errors)
            )

        roadmap: Roadmap | None = result.get(
            "roadmap"
        )

        if roadmap is None:
            raise ValueError(
                "Journey Planner did not return a roadmap."
            )

        journey = Journey(
            title=roadmap.title,
            reason=journey_input.reason,
            goal=roadmap.goal,
            existing_knowledge=(
                journey_input.existing_knowledge
            ),
        )

        for roadmap_topic in roadmap.topics:

            topic = Topic(
                title=roadmap_topic.title,
                description=roadmap_topic.description,
                order=roadmap_topic.order,
            )

            journey.topics.append(topic)

        self.db.add(journey)

        self.db.commit()

        self.db.refresh(journey)

        return journey