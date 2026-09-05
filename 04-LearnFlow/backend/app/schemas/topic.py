from pydantic import BaseModel


class TopicResponse(BaseModel):

    id: int

    title: str

    description: str

    order: int

    completed: bool


class LearningSectionResponse(BaseModel):
    heading: str
    content: str


class LearningContentResponse(BaseModel):
    title: str
    sections: list[LearningSectionResponse]
    key_points: list[str]
    examples: list[str]


class TopicNotesResponse(BaseModel):
    id: int
    topic_id: int
    content: LearningContentResponse


class TopicCompletionResponse(BaseModel):

    id: int

    title: str

    completed: bool