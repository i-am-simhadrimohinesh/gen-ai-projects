import requests
import streamlit as st
def format_markdown(content: str) -> str:
    content = content.replace("```python ", "```python\n")
    content = content.replace("```bash ", "```bash\n")
    content = content.replace("```mermaid ", "```mermaid\n")
    content = content.replace(" ```", "\n```")

    return content

from api_client import (
    get_journeys,
    get_journey,
    create_journey,
    get_topic_notes,
    complete_topic,
    get_assessment_history,
    create_assessment,
    get_assessment,
    submit_assessment,
    delete_journey,
)


st.set_page_config(
    page_title="LearnFlow",
    page_icon="📘",
    layout="wide",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.2);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Delete Journey Dialog
# --------------------------------------------------

@st.dialog("🗑️ Delete Journey")
def delete_journey_dialog(
    journey_id: int,
    journey_title: str,
):
    st.write(
        f'Are you sure you want to delete "{journey_title}"?'
    )

    st.warning(
        "This will permanently delete the journey, "
        "roadmap, learning content, assessments, and "
        "assessment history."
    )

    confirm_col, cancel_col = st.columns(2)

    with confirm_col:

        if st.button(
            "Delete",
            key=f"confirm_delete_{journey_id}",
            type="primary",
            use_container_width=True,
        ):

            try:

                delete_journey(journey_id)

                st.session_state.journeys = get_journeys()

                if (
                    st.session_state.selected_journey_id
                    == journey_id
                ):
                    st.session_state.selected_journey_id = None
                    st.session_state.selected_topic_id = None
                    st.session_state.selected_assessment_id = None
                    st.session_state.assessment_result = None
                    st.session_state.page = "welcome"

                st.rerun()

            except requests.RequestException as exc:

                st.error(
                    f"Unable to delete journey: {exc}"
                )

    with cancel_col:

        if st.button(
            "Cancel",
            key=f"cancel_delete_{journey_id}",
            use_container_width=True,
        ):

            st.rerun()


# --------------------------------------------------
# Session State
# --------------------------------------------------

if "selected_journey_id" not in st.session_state:
    st.session_state.selected_journey_id = None

if "selected_topic_id" not in st.session_state:
    st.session_state.selected_topic_id = None

if "selected_assessment_id" not in st.session_state:
    st.session_state.selected_assessment_id = None

if "assessment_result" not in st.session_state:
    st.session_state.assessment_result = None

if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "journeys" not in st.session_state:

    try:

        st.session_state.journeys = get_journeys()

    except requests.RequestException:

        st.session_state.journeys = []


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        "# 📘 LearnFlow"
    )

    st.caption(
        "Adaptive learning, one topic at a time."
    )

    st.divider()

    st.markdown(
        "**🧭 JOURNEYS**"
    )

    journeys = st.session_state.journeys

    if journeys:

        for journey in journeys:

            col1, col2 = st.columns(
                [5, 1]
            )

            with col1:

                if st.button(
                    journey["title"],
                    key=f"journey_{journey['id']}",
                    use_container_width=True,
                ):

                    st.session_state.selected_journey_id = (
                        journey["id"]
                    )

                    st.session_state.selected_topic_id = None
                    st.session_state.selected_assessment_id = None
                    st.session_state.assessment_result = None
                    st.session_state.page = "journey"

                    st.rerun()

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_{journey['id']}",
                    use_container_width=True,
                ):

                    delete_journey_dialog(
                        journey["id"],
                        journey["title"],
                    )

    else:

        st.info(
            "No journeys yet."
        )

    st.divider()

    if st.button(
        "＋ Create Journey",
        use_container_width=True,
        type="primary",
    ):

        st.session_state.selected_journey_id = None
        st.session_state.selected_topic_id = None
        st.session_state.selected_assessment_id = None
        st.session_state.assessment_result = None
        st.session_state.page = "create"

        st.rerun()


# --------------------------------------------------
# Welcome Page
# --------------------------------------------------

if st.session_state.page == "welcome":

    st.title(
        "Welcome to LearnFlow 👋"
    )

    st.caption(
        "Learn skills through personalized journeys, "
        "practical learning content, and assessments."
    )

    if journeys:

        st.info(
            "🧭 Select a journey from the sidebar to continue learning."
        )

    else:

        st.markdown(
            """
            ### 🚀 Start your first learning journey

            LearnFlow will help you:

            - 🗺️ Build a personalized roadmap
            - 📚 Learn each topic step by step
            - 🧠 Assess your understanding
            - 📊 Identify weak areas
            - 🔄 Improve through future assessments
            """
        )

        st.write("")

        if st.button(
            "＋ Create Your First Journey",
            type="primary",
            use_container_width=False,
        ):

            st.session_state.page = "create"

            st.rerun()


# --------------------------------------------------
# Create Journey Page
# --------------------------------------------------

elif st.session_state.page == "create":

    st.title(
        "Create Journey 🧭"
    )

    st.caption(
        "Tell LearnFlow what you want to learn."
    )

    with st.container(border=True):

        title = st.text_input(
            "🎯 What do you want to learn?",
            placeholder="Example: LangChain",
        )

        reason = st.text_area(
            "💡 Why do you want to learn it?",
            placeholder=(
                "Example: I want to build AI applications."
            ),
        )

        goal = st.text_area(
            "🏁 What is your final goal?",
            placeholder=(
                "Example: Build production-ready LLM "
                "applications using LangChain."
            ),
        )

        existing_knowledge = st.text_area(
            "🧠 What do you already know?",
            placeholder=(
                "Example: I know Python and basic LLM concepts."
            ),
        )

        requested_topics_text = st.text_area(
            "📚 What specifically do you want to learn?",
            placeholder=(
                "Enter one topic per line.\n"
                "Example:\n"
                "LangChain basics\n"
                "Chains\n"
                "Agents\n"
                "RAG"
            ),
        )

    st.write("")

    if st.button(
        "🚀 Create Journey",
        type="primary",
        use_container_width=True,
    ):

        if not title.strip():

            st.error(
                "Please enter what you want to learn."
            )

        elif not reason.strip():

            st.error(
                "Please enter why you want to learn it."
            )

        elif not goal.strip():

            st.error(
                "Please enter your final goal."
            )

        elif not existing_knowledge.strip():

            st.error(
                "Please describe what you already know."
            )

        else:

            requested_topics = [
                topic.strip()
                for topic in requested_topics_text.splitlines()
                if topic.strip()
            ]

            try:

                with st.spinner(
                    "🧠 Preparing your learning journey..."
                ):

                    journey = create_journey(
                        title=title.strip(),
                        reason=reason.strip(),
                        goal=goal.strip(),
                        existing_knowledge=(
                            existing_knowledge.strip()
                        ),
                        requested_topics=requested_topics,
                    )

                st.session_state.journeys = get_journeys()

                st.session_state.selected_journey_id = (
                    journey["id"]
                )

                st.session_state.selected_topic_id = None
                st.session_state.selected_assessment_id = None
                st.session_state.assessment_result = None
                st.session_state.page = "journey"

                st.success(
                    "Journey created successfully."
                )

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

        st.title(
            f"🧭 {journey['title']}"
        )

        st.caption(
            "Your personalized learning journey"
        )

        with st.container(border=True):

            st.markdown(
                "### 🎯 Goal"
            )

            st.write(
                journey["goal"]
            )

        st.write("")

        # ------------------------------------------
        # Roadmap
        # ------------------------------------------

        st.markdown(
            "## 🗺️ Roadmap"
        )

        topics = journey["topics"]

        completed_count = sum(
            1
            for topic in topics
            if topic["completed"]
        )

        total_topics = len(topics)

        if total_topics:

            progress = (
                completed_count / total_topics
            )

            st.progress(
                progress
            )

            st.caption(
                f"{completed_count} of {total_topics} topics completed"
            )

        st.write("")

        for topic in topics:

            completed = topic["completed"]

            with st.container(border=True):

                header_col, status_col = st.columns(
                    [5, 1]
                )

                with header_col:

                    if completed:

                        topic_label = (
                            f"✅ {topic['order']}. "
                            f"{topic['title']}"
                        )

                    else:

                        topic_label = (
                            f"📘 {topic['order']}. "
                            f"{topic['title']}"
                        )

                    if st.button(
                        topic_label,
                        key=f"topic_{topic['id']}",
                        use_container_width=True,
                    ):

                        st.session_state.selected_topic_id = (
                            topic["id"]
                        )

                        st.session_state.page = "topic"

                        st.rerun()

                with status_col:

                    if completed:

                        st.success(
                            "Completed"
                        )

                    else:

                        st.caption(
                            "Pending"
                        )

                st.markdown(
                    topic["description"]
                )

        # ------------------------------------------
        # Assessment History
        # ------------------------------------------

        completed_topics = [
            topic
            for topic in topics
            if topic["completed"]
        ]

        if completed_topics:

            st.write("")

            st.markdown(
                "## 🧠 Assessment History"
            )

            st.caption(
                "Assessments are based only on the topics "
                "you have completed."
            )

            # --------------------------------------
            # Create New Assessment
            # --------------------------------------

            if st.button(
                "＋ Create New Assessment",
                type="primary",
                use_container_width=True,
            ):

                try:

                    with st.spinner(
                        "🧠 Preparing a new assessment..."
                    ):

                        assessment = create_assessment(
                            journey_id=journey["id"]
                        )

                    st.session_state.selected_assessment_id = (
                        assessment["id"]
                    )

                    st.session_state.assessment_result = None
                    st.session_state.page = "assessment"

                    st.rerun()

                except requests.RequestException as exc:

                    st.error(
                        f"Unable to create assessment: {exc}"
                    )

            st.write("")

            # --------------------------------------
            # Assessment History List
            # --------------------------------------

            try:

                assessment_history = (
                    get_assessment_history(
                        journey["id"]
                    )
                )

                if not assessment_history:

                    st.info(
                        "No assessments have been created yet."
                    )

                else:

                    for assessment in assessment_history:

                        assessment_id = assessment["id"]
                        status = assessment["status"]
                        best_score = assessment["best_score"]
                        attempts = assessment["attempts"]

                        with st.container(border=True):

                            col1, col2, col3 = st.columns(
                                [2.5, 1.5, 2]
                            )

                            with col1:

                                st.markdown(
                                    f"### 📝 Assessment "
                                    f"#{assessment['assessment_number']}"
                                )

                                st.caption(
                                    assessment["created_at"]
                                )

                            with col2:

                                if status == "Completed":

                                    st.success(
                                        "Completed"
                                    )

                                else:

                                    st.info(
                                        "Not Attempted"
                                    )

                            with col3:

                                if best_score is not None:

                                    st.metric(
                                        "Best Score",
                                        f"{best_score:.1f}%",
                                    )

                                else:

                                    st.metric(
                                        "Best Score",
                                        "—",
                                    )

                            action_col, attempt_col = st.columns(
                                [2, 1]
                            )

                            with action_col:

                                if status == "Completed":

                                    if st.button(
                                        "🔄 Re-attempt",
                                        key=(
                                            f"reattempt_"
                                            f"{assessment_id}"
                                        ),
                                        use_container_width=True,
                                    ):

                                        st.session_state.selected_assessment_id = (
                                            assessment_id
                                        )

                                        st.session_state.assessment_result = None
                                        st.session_state.page = "assessment"

                                        st.rerun()

                                else:

                                    if st.button(
                                        "▶️ Start Assessment",
                                        key=(
                                            f"start_"
                                            f"{assessment_id}"
                                        ),
                                        use_container_width=True,
                                    ):

                                        st.session_state.selected_assessment_id = (
                                            assessment_id
                                        )

                                        st.session_state.assessment_result = None
                                        st.session_state.page = "assessment"

                                        st.rerun()

                            with attempt_col:

                                st.caption(
                                    f"Attempts: {attempts}"
                                )

            except requests.RequestException as exc:

                st.error(
                    f"Unable to load assessment history: {exc}"
                )

    except requests.RequestException as exc:

        st.error(
            f"Unable to load the selected journey: {exc}"
        )


# --------------------------------------------------
# Assessment Page
# --------------------------------------------------

elif st.session_state.page == "assessment":

    try:

        if (
            st.session_state.selected_assessment_id
            is None
        ):

            st.error(
                "No assessment has been selected."
            )

            if st.button(
                "← Back to Journey",
                use_container_width=True,
            ):

                st.session_state.page = "journey"

                st.rerun()

        else:

            assessment = get_assessment(
                st.session_state.selected_assessment_id
            )

            st.title(
                f"🧠 Assessment #{assessment['assessment_number']}"
            )

            st.caption(
                "Test your understanding of the topics you have completed."
            )

            st.info(
                f"📋 {len(assessment['questions'])} questions"
            )

            st.divider()

            for index, question in enumerate(
                assessment["questions"],
                start=1,
            ):

                with st.container(border=True):

                    st.markdown(
                        f"### Question {index}"
                    )

                    st.markdown(
                        question["question"]
                    )

                    st.radio(
                        "Select your answer:",
                        question["options"],
                        key=(
                            f"assessment_"
                            f"{assessment['id']}_"
                            f"question_"
                            f"{question['id']}"
                        ),
                    )

            st.write("")

            if st.button(
                "🚀 Submit Assessment",
                type="primary",
                use_container_width=True,
            ):

                answers = []

                for question in assessment["questions"]:

                    selected_answer = st.session_state.get(
                        (
                            f"assessment_"
                            f"{assessment['id']}_"
                            f"question_"
                            f"{question['id']}"
                        )
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
                            "🔍 Evaluating your assessment..."
                        ):

                            result = submit_assessment(
                                assessment_id=assessment["id"],
                                answers=answers,
                            )

                        st.session_state.assessment_result = (
                            result
                        )

                        st.session_state.page = (
                            "assessment_result"
                        )

                        st.rerun()

                    except requests.RequestException as exc:

                        st.error(
                            f"Unable to submit assessment: {exc}"
                        )

            st.divider()

            if st.button(
                "← Back to Journey",
                use_container_width=True,
            ):

                st.session_state.selected_assessment_id = None
                st.session_state.page = "journey"

                st.rerun()

    except requests.RequestException as exc:

        st.error(
            f"Unable to load assessment: {exc}"
        )


# --------------------------------------------------
# Assessment Result Page
# --------------------------------------------------

elif st.session_state.page == "assessment_result":

    result = st.session_state.get(
        "assessment_result"
    )

    if result is None:

        st.error(
            "Assessment result is not available."
        )

        if st.button(
            "← Back to Journey",
            use_container_width=True,
        ):

            st.session_state.page = "journey"

            st.rerun()

    else:

        st.title(
            "🎯 Assessment Result"
        )

        st.caption(
            "Here is how you performed."
        )

        # ------------------------------------------
        # Overall Result
        # ------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🏆 Score",
                f"{result['score']:.1f}%",
            )

        with col2:

            st.metric(
                "✅ Correct",
                (
                    f"{result['correct_answers']} "
                    f"/ {result['total_questions']}"
                ),
            )

        with col3:

            st.metric(
                "📝 Answered",
                (
                    f"{result['answered_questions']} "
                    f"/ {result['total_questions']}"
                ),
            )

        st.divider()

        # ------------------------------------------
        # Question Results
        # ------------------------------------------

        st.markdown(
            "## 📋 Question Results"
        )

        for index, question_result in enumerate(
            result["question_results"],
            start=1,
        ):

            if question_result["correct"]:

                with st.container(border=True):

                    st.success(
                        f"Question {index} — Correct"
                    )

                    st.caption(
                        f"Topic: {question_result['topic']}"
                    )

            else:

                with st.container(border=True):

                    st.error(
                        f"Question {index} — Incorrect"
                    )

                    st.caption(
                        f"Topic: {question_result['topic']}"
                    )

        st.divider()

        # ------------------------------------------
        # Topic Performance
        # ------------------------------------------

        topic_stats = {}

        for question_result in result[
            "question_results"
        ]:

            topic = question_result["topic"]

            if topic not in topic_stats:

                topic_stats[topic] = {
                    "correct": 0,
                    "total": 0,
                }

            topic_stats[topic]["total"] += 1

            if question_result["correct"]:

                topic_stats[topic]["correct"] += 1

        st.markdown(
            "## 📊 Topic Performance"
        )

        for topic, stats in topic_stats.items():

            topic_score = (
                stats["correct"]
                / stats["total"]
                * 100
            )

            with st.container(border=True):

                st.markdown(
                    f"**{topic}**"
                )

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

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "← Back to Journey",
                type="primary",
                use_container_width=True,
            ):

                st.session_state.page = "journey"
                st.session_state.assessment_result = None
                st.session_state.selected_assessment_id = None

                st.rerun()

        with col2:

            if st.button(
                "🔄 Re-attempt Assessment",
                use_container_width=True,
            ):

                st.session_state.assessment_result = None
                st.session_state.page = "assessment"

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

        st.title(
            f"📚 {content['title']}"
        )

        st.caption(
            "Learn the topic step by step."
        )

        st.divider()

        # ------------------------------------------
        # Notes
        # ------------------------------------------

        for index, section in enumerate(
            content.get(
                "sections",
                [],
            ),
            start=1,
        ):

            with st.container(border=True):

                st.markdown(
                    f"### {section['heading']}"
                )

                # Generated Markdown, code blocks,
                # tables, lists, etc. render properly.
                st.markdown(
                    format_markdown(section["content"])
                )

        # ------------------------------------------
        # Key Points
        # ------------------------------------------

        if content.get("key_points"):

            st.divider()

            with st.container(border=True):

                st.markdown(
                    "## 💡 Key Points"
                )

                for point in content["key_points"]:

                    st.markdown(
                        f"- {point}"
                    )

        # ------------------------------------------
        # Examples
        # ------------------------------------------

        if content.get("examples"):

            st.divider()

            with st.container(border=True):

                st.markdown(
                    "## 💻 Examples"
                )

                for example in content["examples"]:

                    st.markdown(
                        f"- {example}"
                    )

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

            notes = content["title"] + "\n\n"

            for section in content.get("sections", []):

                notes += (
                    f"{section['heading']}\n\n"
                    f"{section['content']}\n\n"
                )

            if content.get("key_points"):

                notes += "Key Points\n\n"

                for point in content["key_points"]:

                    notes += f"- {point}\n"

            if content.get("examples"):

                notes += "\nExamples\n\n"

                for example in content["examples"]:

                    notes += f"- {example}\n"

            st.download_button(
                "⬇️ Download Notes",
                data=notes,
                file_name="learning_notes.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with col3:

            if st.button(
                "✅ Complete Topic",
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