from app.llm.provider import get_llm

from app.workflows.notes_generator.graph import (
    build_notes_generator_graph,
)


def test_notes_generator_creates_learning_content():
    llm = get_llm()

    notes_generator = build_notes_generator_graph(llm)

    state = {
        "topic": {
            "title": "Introduction to LangChain Core Concepts",
            "description": (
                "Understand the fundamental building blocks "
                "of LangChain, including LLMs, prompts, output "
                "parsers, and chains."
            ),
        },
        "generation_attempts": 0,
        "validation_errors": [],
    }

    result = notes_generator.invoke(state)

    assert result["subtopics"]
    assert result["learning_content"] is not None

    learning_content = result["learning_content"]

    assert learning_content.title
    assert learning_content.sections
    assert learning_content.key_points
    assert isinstance(learning_content.examples, list)

    assert result["generation_attempts"] >= 1
    assert result["validation_errors"] == []