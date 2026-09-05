from pydantic import BaseModel, Field

from app.schemas.topic import TopicResponse


class CreateJourneyRequest(BaseModel):

    title: str = Field(
        min_length=1
    )

    reason: str = Field(
        min_length=1
    )

    goal: str = Field(
        min_length=1
    )

    existing_knowledge: str = Field(
        min_length=1
    )

    requested_topics: list[str] = Field(
        default_factory=list
    )


class JourneyResponse(BaseModel):

    id: int

    title: str

    reason: str

    goal: str

    existing_knowledge: str

    topics: list[TopicResponse]


class JourneySummaryResponse(BaseModel):

    id: int

    title: str

    goal: str