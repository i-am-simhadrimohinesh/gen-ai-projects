from typing import TypedDict

from .schemas import LearningContent


class NotesState(TypedDict, total=False):

    topic: dict

    subtopics: list[str]

    learning_content: LearningContent

    validation_errors: list[str]

    generation_attempts: int