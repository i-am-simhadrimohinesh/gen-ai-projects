from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph

from .nodes import (
    create_notes_generator,
    create_subtopics_generator,
    route_after_notes_validation,
    validate_notes,
)
from .state import NotesState


def build_notes_generator_graph(
    llm: BaseChatModel,
):

    builder = StateGraph(NotesState)

    generate_subtopics = (
        create_subtopics_generator(llm)
    )

    generate_notes = (
        create_notes_generator(llm)
    )

    builder.add_node(
        "generate_subtopics",
        generate_subtopics,
    )

    builder.add_node(
        "generate_notes",
        generate_notes,
    )

    builder.add_node(
        "validate_notes",
        validate_notes,
    )

    builder.add_edge(
        START,
        "generate_subtopics",
    )

    builder.add_edge(
        "generate_subtopics",
        "generate_notes",
    )

    builder.add_edge(
        "generate_notes",
        "validate_notes",
    )

    builder.add_conditional_edges(
        "validate_notes",
        route_after_notes_validation,
        {
            "retry": "generate_notes",
            "complete": END,
            "failed": END,
        },
    )

    return builder.compile()