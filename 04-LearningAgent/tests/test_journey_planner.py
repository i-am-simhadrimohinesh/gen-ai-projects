from app.llm.provider import get_llm
from app.workflows.journey_planner.graph import (
    build_journey_planner_graph,
)
from app.workflows.journey_planner.schemas import (
    CreateJourneyRequest,
)


def main():

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

    print("\n=== ROADMAP ===\n")

    roadmap = result.get("roadmap")

    if roadmap:
        print(
            f"Title: {roadmap.title}"
        )

        print(
            f"Goal: {roadmap.goal}"
        )

        print("\nTopics:")

        for topic in roadmap.topics:
            print(
                f"{topic.order}. "
                f"{topic.title}"
            )
            print(
                f"   {topic.description}"
            )

    errors = result.get(
        "validation_errors",
        [],
    )

    if errors:
        print("\n=== VALIDATION ERRORS ===")

        for error in errors:
            print(f"- {error}")

    print(
        f"\nRetry count: "
        f"{result.get('retry_count', 0)}"
    )


if __name__ == "__main__":
    main()