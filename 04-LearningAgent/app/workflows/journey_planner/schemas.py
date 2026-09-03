from pydantic import BaseModel, Field


class CreateJourneyRequest(BaseModel):
    title: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    existing_knowledge: str = Field(min_length=1)
    requested_topics: list[str] = Field(default_factory=list)


class RoadmapTopic(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    order: int = Field(ge=1)


class Roadmap(BaseModel):
    title: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    topics: list[RoadmapTopic] = Field(min_length=3)