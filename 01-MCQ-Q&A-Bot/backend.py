from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',temperature=0.8)
class Question(BaseModel):
    question: str
    options: List[str]
    actualAnswer: str

class QuestionList(BaseModel):
    questions: List[Question]

structured_model = model.with_structured_output(QuestionList)
