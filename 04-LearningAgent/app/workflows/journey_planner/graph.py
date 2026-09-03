from langgraph.graph import END, START, StateGraph
from langchain_core.language_models import BaseChatModel

from .nodes import (
    create_roadmap_generator,
    route_after_validation,
    validate_roadmap,
)
from .state import JourneyPlannerState


def build_journey_planner_graph(
    llm: BaseChatModel,
):

    builder = StateGraph(JourneyPlannerState)

    generate_roadmap = create_roadmap_generator(llm)

    builder.add_node(
        "generate_roadmap",
        generate_roadmap,
    )

    builder.add_node(
        "validate_roadmap",
        validate_roadmap,
    )

    builder.add_edge(
        START,
        "generate_roadmap",
    )

    builder.add_edge(
        "generate_roadmap",
        "validate_roadmap",
    )

    builder.add_conditional_edges(
        "validate_roadmap",
        route_after_validation,
        {
            "retry": "generate_roadmap",
            "complete": END,
            "failed": END,
        },
    )

    return builder.compile()