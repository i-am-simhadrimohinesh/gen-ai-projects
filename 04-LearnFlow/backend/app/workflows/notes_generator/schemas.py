from pydantic import BaseModel, Field


class Subtopics(BaseModel):

    subtopics: list[str] = Field(
        min_length=1
    )


class LearningSection(BaseModel):

    heading: str = Field(
        min_length=1
    )

    content: str = Field(
        min_length=1
    )


class LearningContent(BaseModel):

    title: str = Field(
        min_length=1
    )

    sections: list[LearningSection] = Field(
        min_length=1
    )

    key_points: list[str] = Field(
        min_length=1
    )

    examples: list[str] = Field(
        default_factory=list
    )