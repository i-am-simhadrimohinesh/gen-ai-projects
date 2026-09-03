from app.db.database import SessionLocal
from app.services.learning_service import LearningService


def main():
    db = SessionLocal()

    try:
        journey_id = 1  # Change this to your journey ID

        service = LearningService(db)

        context = service.get_assessment_context(journey_id)

        print()
        print("=" * 60)
        print("ASSESSMENT CONTEXT")
        print("=" * 60)

        print("\nJourney:")
        print(context["journey"])

        print("\nCovered Topics:")
        for topic in context["covered_topics"]:
            print(
                f"  {topic['order']}. "
                f"{topic['title']}"
            )

        print("\nWeak Topics:")
        for topic in context["weak_topics"]:
            print(
                f"  {topic['topic']} "
                f"-> {topic['score']}%"
            )

        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()