from sqlalchemy.orm import Session

from app.db.models import Journey, Topic, LearningContent, LearnerKnowledge
from app.llm.provider import get_llm
from app.workflows.notes_generator.graph import (
    build_notes_generator_graph,
)

WEAK_TOPIC_THRESHOLD = 60.0

class LearningService:
    def __init__(self, db: Session):

        self.db = db

        self.notes_generator = None

    def get_topic_notes(
        self,
        topic_id: int,
    ) -> LearningContent:

        topic = (
            self.db.query(Topic)
            .filter(Topic.id == topic_id)
            .first()
        )

        if topic is None:
            raise ValueError(
                "Topic not found."
            )

        # Check whether notes already exist

        learning_content = (
            self.db.query(LearningContent)
            .filter(
                LearningContent.topic_id == topic_id
            )
            .first()
        )

        if learning_content is not None:
            return learning_content

        # Notes do not exist.
        # Generate them using LangGraph.

        state = {
            "topic": {
                "title": topic.title,
                "description": topic.description,
            },
            "generation_attempts": 0,
            "validation_errors": [],
        }
        if self.notes_generator is None:
            llm = get_llm()
            self.notes_generator = build_notes_generator_graph(llm)

        result = self.notes_generator.invoke(
            state
        )

        validation_errors = result.get(
            "validation_errors",
            [],
        )

        if validation_errors:

            raise ValueError(
                "Unable to generate valid notes: "
                + "; ".join(validation_errors)
            )

        generated_content = result.get(
            "learning_content"
        )

        if generated_content is None:

            raise ValueError(
                "Notes Generator did not return "
                "learning content."
            )

        # Save generated content

        learning_content = LearningContent(
            topic_id=topic_id,
            content=generated_content.model_dump(),
        )

        self.db.add(
            learning_content
        )

        self.db.commit()

        self.db.refresh(
            learning_content
        )

        return learning_content

    def complete_topic(
    self,
    topic_id: int,
    ) -> Topic:

        topic = (
            self.db.query(Topic)
            .filter(Topic.id == topic_id)
            .first()
        )

        if topic is None:
            raise ValueError(
                "Topic not found."
            )

        topic.completed = True

        self.db.commit()

        self.db.refresh(topic)

        return topic
    def get_completed_topics(
    self,
    journey_id: int,
    ) -> list[Topic]:

        return (
            self.db.query(Topic)
            .filter(
                Topic.journey_id == journey_id,
                Topic.completed.is_(True),
            )
            .order_by(Topic.order)
            .all()
        )
    def get_assessment_context(
        self,
        journey_id: int,
        ) -> dict:

        journey = (
            self.db.query(Journey)
            .filter(Journey.id == journey_id)
            .first()
        )

        if journey is None:
            raise ValueError(
                "Journey not found."
            )

        completed_topics = self.get_completed_topics(
            journey_id
        )

        if not completed_topics:
            raise ValueError(
                "No completed topics available for assessment."
            )
        weak_topics = self.get_weak_topics(journey_id)
        return {
            "journey": {
                "title": journey.title,
                "goal": journey.goal,
            },
            "covered_topics": [
                {
                    "title": topic.title,
                    "description": topic.description,
                    "order": topic.order,
                }
                for topic in completed_topics
            ],
            "weak_topics": weak_topics,
        }
    def get_weak_topics(self, journey_id: int) -> list[dict]:
        weak_topics = (
            self.db.query(LearnerKnowledge)
            .filter(
                LearnerKnowledge.journey_id == journey_id,
                LearnerKnowledge.best_score < WEAK_TOPIC_THRESHOLD,
            )
            .order_by(LearnerKnowledge.best_score.asc())
            .all()
        )

        return [
            {
                "topic": knowledge.topic,
                "score": knowledge.best_score,
            }
            for knowledge in weak_topics
        ]