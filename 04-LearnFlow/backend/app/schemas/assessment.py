from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class AssessmentAnswer(BaseModel):

    question_id: int = Field(gt=0)

    selected_answer: str = Field(min_length=1)


class AssessmentSubmission(BaseModel):

    answers: list[AssessmentAnswer] = Field(min_length=1)


class QuestionResult(BaseModel):

    question_id: int

    topic: str

    correct: bool


class AssessmentResult(BaseModel):

    assessment_id: int

    total_questions: int

    answered_questions: int

    correct_answers: int

    score: float

    question_results: list[QuestionResult]


class AssessmentQuestionResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    question: str
    options: list[str]
    topic: str
    difficulty: str
    order: int


class AssessmentAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    score: float

    total_questions: int

    answered_questions: int

    correct_answers: int

    created_at: datetime


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    journey_id: int
    assessment_number: int
    created_at: datetime
    questions: list[AssessmentQuestionResponse]
    attempts: list[AssessmentAttemptResponse] = Field(
        default_factory=list
    )


class AssessmentHistoryItem(BaseModel):
    id: int
    assessment_number: int
    created_at: datetime
    status: Literal["Completed","Not Attempted",]
    best_score: float | None
    attempts: int