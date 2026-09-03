from fastapi import FastAPI

from app.api.journeys import router as journeys_router
from app.api.topics import router as topics_router
from app.api.assessments import router as assessments_router

app = FastAPI(
    title="LearnFlow",
    description="Adaptive AI Learning Platform",
    version="0.1.0",
)


app.include_router(
    journeys_router
)

app.include_router(
    topics_router
)

app.include_router(
    assessments_router
    )