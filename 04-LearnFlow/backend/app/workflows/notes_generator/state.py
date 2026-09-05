from typing import Annotated, TypedDict

import operator

from .schemas import LearningContent


class NotesState(TypedDict, total=False):

    topic: dict

    subtopics: list[str]

    subtopic_contents: Annotated[
        list[tuple[int, LearningContent]],
        operator.add,
    ]

    learning_content: LearningContent

    validation_errors: list[str]

    generation_attempts: int