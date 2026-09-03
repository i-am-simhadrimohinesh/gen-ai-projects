import requests
import streamlit as st

from api_client import (
    get_journeys,
    get_journey,
    create_journey,
    get_topic_notes,
    download_topic_notes,
    complete_topic,
    get_assessment,
    submit_assessment,
)

st.set_page_config(
    page_title="LearnFlow",
    page_icon="📘",
    layout="wide",
)


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "selected_journey_id" not in st.session_state:
    st.session_state.selected_journey_id = None

if "selected_topic_id" not in st.session_state:
    st.session_state.selected_topic_id = None

if "page" not in st.session_state:
    st.session_state.page = "welcome"


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("LearnFlow")
st.sidebar.subheader("JOURNEYS")


try:
    journeys = get_journeys()
except requests.RequestException:
    st.sidebar.error("Unable to connect to FastAPI.")
    journeys = []


if journeys:
    for journey in journeys:
        if st.sidebar.button(
            f"📘 {journey['title']}",
            key=f"journey_{journey['id']}",
            use_container_width=True,
        ):
            st.session_state.selected_journey_id = journey["id"]
            st.session_state.page = "journey"
            st.rerun()
else:
    st.sidebar.info("No journeys yet.")


st.sidebar.divider()


if st.sidebar.button(
    "＋ Create Journey",
    use_container_width=True,
):
    st.session_state.selected_journey_id = None
    st.session_state.page = "create"
    st.rerun()


# --------------------------------------------------
# Welcome Page
# --------------------------------------------------

if st.session_state.page == "welcome":

    st.title("Welcome to LearnFlow")

    st.write(
        "Select a journey from the sidebar to continue learning."
    )


# --------------------------------------------------
# Create Journey Page
# --------------------------------------------------

elif st.session_state.page == "create":

    st.title("Create Journey")

    st.write(
        "Tell LearnFlow what you want to learn."
    )

    title = st.text_input(
        "What do you want to learn?",
        placeholder="Example: LangChain",
    )

    reason = st.text_area(
        "Why do you want to learn it?",
        placeholder="Example: I want to build AI applications.",
    )

    goal = st.text_area(
        "What is your final goal?",
        placeholder="Example: Build production-ready LLM applications using LangChain.",
    )

    existing_knowledge = st.text_area(
        "What do you already know?",
        placeholder="Example: I know Python and basic LLM concepts.",
    )

    requested_topics_text = st.text_area(
        "What specifically do you want to learn?",
        placeholder=(
            "Enter one topic per line.\n"
            "Example:\n"
            "LangChain basics\n"
            "Chains\n"
            "Agents\n"
            "RAG"
        ),
    )

    if st.button(
        "Create Journey",
        type="primary",
        use_container_width=True,
    ):

        if not title.strip():
            st.error("Please enter what you want to learn.")

        elif not reason.strip():
            st.error("Please enter why you want to learn it.")

        elif not goal.strip():
            st.error("Please enter your final goal.")

        elif not existing_knowledge.strip():
            st.error("Please describe what you already know.")

        else:

            requested_topics = [
                topic.strip()
                for topic in requested_topics_text.splitlines()
                if topic.strip()
            ]

            try:

                with st.spinner(
                    "Preparing your learning journey..."
                ):
                    journey = create_journey(
                        title=title.strip(),
                        reason=reason.strip(),
                        goal=goal.strip(),
                        existing_knowledge=existing_knowledge.strip(),
                        requested_topics=requested_topics,
                    )

                st.session_state.selected_journey_id = journey["id"]
                st.session_state.page = "journey"

                st.success("Journey created successfully.")

                st.rerun()

            except requests.RequestException as exc:

                st.error(
                    f"Unable to create journey: {exc}"
                )


# --------------------------------------------------
# Journey Page
# --------------------------------------------------

elif st.session_state.page == "journey":

    try:

        journey = get_journey(
            st.session_state.selected_journey_id
        )

        st.title(journey["title"])

        st.subheader("Goal")

        st.write(journey["goal"])

        st.divider()

        st.subheader("Roadmap")

        for topic in journey["topics"]:

            status = (
                "✅ Completed"
                if topic["completed"]
                else "⬜ Pending"
            )

            if st.button(
                f"{topic['order']}. {topic['title']}",
                key=f"topic_{topic['id']}",
                use_container_width=True,
            ):
                st.session_state.selected_topic_id = topic["id"]
                st.session_state.page = "topic"
                st.rerun()

            st.write(topic["description"])
            st.caption(status)

            st.divider()
        # ------------------------------------------
        # Assessment
        # ------------------------------------------

        completed_topics = [
            topic
            for topic in journey["topics"]
            if topic["completed"]
        ]

        if completed_topics:

            st.subheader("Assessment")

            st.write(
                "Test your understanding of the topics you have completed."
            )

            if st.button(
                "Start Assessment",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "assessment"
                st.rerun()

    except requests.RequestException:

        st.error(
            "Unable to load the selected journey."
        )


# --------------------------------------------------
# Assessment Page
# --------------------------------------------------

elif st.session_state.page == "assessment":

    try:

        assessment = get_assessment(
            st.session_state.selected_journey_id
        )

        st.title("Assessment")

        st.write(
            "Answer the following questions based on the topics you have completed."
        )

        st.divider()

        for index, question in enumerate(
            assessment["questions"],
            start=1,
        ):

            st.subheader(
                f"Question {index}"
            )

            st.write(
                question["question"]
            )

            st.radio(
                "Select your answer:",
                question["options"],
                key=f"assessment_question_{question['id']}",
            )

            st.divider()

        if st.button(
            "Submit Assessment",
            type="primary",
            use_container_width=True,
        ):

            answers = []

            for question in assessment["questions"]:

                selected_answer = st.session_state.get(
                    f"assessment_question_{question['id']}"
                )

                if selected_answer is not None:

                    answers.append(
                        {
                            "question_id": question["id"],
                            "selected_answer": selected_answer,
                        }
                    )

            if not answers:

                st.warning(
                    "Please answer at least one question."
                )

            else:

                try:

                    with st.spinner(
                        "Evaluating your assessment..."
                    ):

                        result = submit_assessment(
                            assessment_id=assessment["id"],
                            answers=answers,
                        )

                    st.session_state.assessment_result = result
                    st.session_state.page = "assessment_result"
                    st.rerun()

                except requests.RequestException as exc:

                    st.error(
                        f"Unable to submit assessment: {exc}"
                    )

    except requests.RequestException as exc:

        st.error(
            f"Unable to load assessment: {exc}"
        )

# --------------------------------------------------
# Assessment Result Page
# --------------------------------------------------

elif st.session_state.page == "assessment_result":

    result = st.session_state.get("assessment_result")

    if result is None:

        st.error("Assessment result is not available.")

        if st.button(
            "← Back to Journey",
            use_container_width=True,
        ):
            st.session_state.page = "journey"
            st.rerun()

    else:

        st.title("Assessment Result")

        st.divider()

        # ------------------------------------------
        # Overall Result
        # ------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Score",
                f"{result['score']:.1f}%",
            )

        with col2:

            st.metric(
                "Correct Answers",
                f"{result['correct_answers']} / {result['total_questions']}",
            )

        with col3:

            st.metric(
                "Answered",
                f"{result['answered_questions']} / {result['total_questions']}",
            )

        st.divider()

        # ------------------------------------------
        # Question Results
        # ------------------------------------------

        st.subheader("Question Results")

        for index, question_result in enumerate(
            result["question_results"],
            start=1,
        ):

            if question_result["correct"]:

                st.success(
                    f"Question {index} — Correct\n\n"
                    f"Topic: {question_result['topic']}"
                )

            else:

                st.error(
                    f"Question {index} — Incorrect\n\n"
                    f"Topic: {question_result['topic']}"
                )

        st.divider()

        # ------------------------------------------
        # Topic Performance
        # ------------------------------------------

        topic_stats = {}

        for question_result in result["question_results"]:

            topic = question_result["topic"]

            if topic not in topic_stats:

                topic_stats[topic] = {
                    "correct": 0,
                    "total": 0,
                }

            topic_stats[topic]["total"] += 1

            if question_result["correct"]:
                topic_stats[topic]["correct"] += 1

        st.subheader("Topic Performance")

        for topic, stats in topic_stats.items():

            topic_score = (
                stats["correct"]
                / stats["total"]
                * 100
            )

            st.write(topic)

            st.progress(
                topic_score / 100
            )

            st.caption(
                f"{stats['correct']} / {stats['total']} correct "
                f"({topic_score:.1f}%)"
            )

        st.divider()

        # ------------------------------------------
        # Navigation
        # ------------------------------------------

        if st.button(
            "← Back to Journey",
            type="primary",
            use_container_width=True,
        ):

            st.session_state.page = "journey"
            st.session_state.assessment_result = None
            st.rerun()
# --------------------------------------------------
# Topic Learning Page
# --------------------------------------------------

elif st.session_state.page == "topic":

    try:

        topic_response = get_topic_notes(
            st.session_state.selected_topic_id
        )

        content = topic_response["content"]

        st.title(content["title"])

        st.divider()

        # ------------------------------------------
        # Notes
        # ------------------------------------------

        for section in content.get("sections", []):

            st.subheader(section["heading"])

            st.write(section["content"])

        # ------------------------------------------
        # Key Points
        # ------------------------------------------

        if content.get("key_points"):

            st.subheader("Key Points")

            for point in content["key_points"]:
                st.markdown(f"- {point}")

        # ------------------------------------------
        # Examples
        # ------------------------------------------

        if content.get("examples"):

            st.subheader("Examples")

            for example in content["examples"]:
                st.markdown(f"- {example}")

        st.divider()

        # ------------------------------------------
        # Actions
        # ------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button(
                "← Back to Roadmap",
                use_container_width=True,
            ):
                st.session_state.page = "journey"
                st.session_state.selected_topic_id = None
                st.rerun()

        with col2:

            try:

                notes_content, content_disposition = (
                    download_topic_notes(
                        st.session_state.selected_topic_id
                    )
                )

                filename = "learning_notes.md"

                if "filename=" in content_disposition:

                    filename = (
                        content_disposition
                        .split("filename=")[-1]
                        .strip('"')
                    )

                st.download_button(
                    "Download Notes",
                    data=notes_content,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True,
                )

            except requests.RequestException:

                st.error(
                    "Unable to prepare notes for download."
                )

        with col3:

            if st.button(
                "Complete Topic",
                type="primary",
                use_container_width=True,
            ):

                try:

                    complete_topic(
                        st.session_state.selected_topic_id
                    )

                    st.success(
                        "Topic completed successfully."
                    )

                    st.session_state.page = "journey"
                    st.session_state.selected_topic_id = None

                    st.rerun()

                except requests.RequestException as exc:

                    st.error(
                        f"Unable to complete topic: {exc}"
                    )

    except requests.RequestException as exc:

        st.error(
            f"Unable to load learning content: {exc}"
        )