from typing import Literal

from pydantic import BaseModel, Field


class AssessmentQuestion(BaseModel):

    question: str = Field(
        min_length=1
    )

    options: list[str] = Field(
        min_length=4,
        max_length=4
    )

    correct_answer: str = Field(
        min_length=1
    )

    topic: str = Field(
        min_length=1
    )

    difficulty: Literal[
        "easy",
        "medium",
        "hard",
    ]


class Assessment(BaseModel):

    questions: list[AssessmentQuestion] = Field(
        min_length=10,
        max_length=10,
    )