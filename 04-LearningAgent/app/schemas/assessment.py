from pydantic import BaseModel, Field


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