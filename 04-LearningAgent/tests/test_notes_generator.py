from app.llm.provider import get_llm

from app.workflows.notes_generator.graph import (
    build_notes_generator_graph,
)


def main():

    llm = get_llm()

    notes_generator = (
        build_notes_generator_graph(llm)
    )

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

    print("\n=== SUBTOPICS ===")

    for index, subtopic in enumerate(
        result["subtopics"],
        start=1,
    ):
        print(f"{index}. {subtopic}")

    learning_content = result[
        "learning_content"
    ]

    print("\n=== LEARNING CONTENT ===")

    print(
        f"\nTitle: {learning_content.title}"
    )

    print("\nSections:")

    for section in learning_content.sections:

        print(
            f"\n### {section.heading}"
        )

        print(section.content)

    print("\nKey Points:")

    for point in learning_content.key_points:

        print(f"- {point}")

    print("\nExamples:")

    for example in learning_content.examples:

        print(f"- {example}")

    print(
        "\nGeneration attempts:",
        result.get("generation_attempts"),
    )

    print(
        "Validation errors:",
        result.get("validation_errors"),
    )


if __name__ == "__main__":
    main()