from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from .nodes import (
    create_subtopic_notes_generator,
    create_subtopics_generator,
    merge_subtopic_notes,
    route_after_notes_validation,
    validate_notes,
)
from .state import NotesState


def fan_out_subtopics(
    state: NotesState,
):

    topic = state["topic"]
    subtopics = state["subtopics"]

    return [
        Send(
            "generate_subtopic_notes",
            {
                "topic": topic,
                "subtopic": subtopic,
                "subtopic_index": index,
            },
        )
        for index, subtopic in enumerate(subtopics)
    ]


def route_after_validation(
    state: NotesState,
):

    route = route_after_notes_validation(
        state
    )

    if route == "complete":

        return END

    if route == "failed":

        return END

    topic = state["topic"]
    subtopics = state["subtopics"]

    return [
        Send(
            "generate_subtopic_notes",
            {
                "topic": topic,
                "subtopic": subtopic,
                "subtopic_index": index,
            },
        )
        for index, subtopic in enumerate(subtopics)
    ]


def build_notes_generator_graph(
    llm: BaseChatModel,
):

    builder = StateGraph(NotesState)

    generate_subtopics = (
        create_subtopics_generator(llm)
    )

    generate_subtopic_notes = (
        create_subtopic_notes_generator(llm)
    )

    builder.add_node(
        "generate_subtopics",
        generate_subtopics,
    )

    builder.add_node(
        "generate_subtopic_notes",
        generate_subtopic_notes,
    )

    builder.add_node(
        "merge_subtopic_notes",
        merge_subtopic_notes,
    )

    builder.add_node(
        "validate_notes",
        validate_notes,
    )

    builder.add_edge(
        START,
        "generate_subtopics",
    )

    builder.add_conditional_edges(
        "generate_subtopics",
        fan_out_subtopics,
    )

    builder.add_edge(
        "generate_subtopic_notes",
        "merge_subtopic_notes",
    )

    builder.add_edge(
        "merge_subtopic_notes",
        "validate_notes",
    )

    builder.add_conditional_edges(
        "validate_notes",
        route_after_validation,
    )

    return builder.compile()