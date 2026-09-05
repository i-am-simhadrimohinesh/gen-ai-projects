from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph

from .nodes import (
    create_assessment_generator,
    route_after_assessment_validation,
    validate_assessment,
)
from .state import AssessmentState


def build_assessment_generator_graph(
    llm: BaseChatModel,
):

    builder = StateGraph(AssessmentState)

    generate_assessment = (
        create_assessment_generator(llm)
    )

    builder.add_node(
        "generate_assessment",
        generate_assessment,
    )

    builder.add_node(
        "validate_assessment",
        validate_assessment,
    )

    builder.add_edge(
        START,
        "generate_assessment",
    )

    builder.add_edge(
        "generate_assessment",
        "validate_assessment",
    )

    builder.add_conditional_edges(
        "validate_assessment",
        route_after_assessment_validation,
        {
            "retry": "generate_assessment",
            "complete": END,
            "failed": END,
        },
    )

    return builder.compile()