from app.llm.provider import get_llm

from app.workflows.journey_planner.graph import (
    build_journey_planner_graph,
)
from app.schemas.journey import CreateJourneyRequest
from app.workflows.journey_planner.schemas import Roadmap


def test_journey_planner_creates_valid_roadmap():
    llm = get_llm()

    graph = build_journey_planner_graph(llm)

    journey_input = CreateJourneyRequest(
        title="LangChain",
        reason="I want to build GenAI applications",
        goal=(
            "Build production-ready GenAI applications "
            "using LangChain"
        ),
        existing_knowledge=(
            "Python and basic LLM concepts"
        ),
        requested_topics=[
            "LangChain",
            "LangGraph",
            "RAG",
        ],
    )

    initial_state = {
        "journey_input": journey_input,
        "retry_count": 0,
    }

    result = graph.invoke(initial_state)

    assert result.get("roadmap") is not None

    roadmap = result["roadmap"]

    assert roadmap.title
    assert roadmap.goal
    assert roadmap.topics
    assert len(roadmap.topics) >= 3

    assert result.get("validation_errors", []) == []

    assert result.get("retry_count", 0) >= 0

    for index, topic in enumerate(
        roadmap.topics,
        start=1,
    ):
        assert topic.order == index
        assert topic.title
        assert topic.description