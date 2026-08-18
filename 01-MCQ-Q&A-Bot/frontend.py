from backend import structured_model
import streamlit as st

st.title("🧠 Welcome to the Q&A Challenge")
if "Q&AList" not in st.session_state : 
    number_of_questions = 5
    topic = "Linux Beginner" # Give your interested topic
    with st.spinner("🤖 Generating your questions... Please wait ⏳"):
        response = structured_model.invoke(f"""You are an expert quiz generator.

Generate {number_of_questions} multiple-choice questions on the topic: {topic}.

Follow these rules strictly:

1. Each question must have exactly 4 options.
2. Only one option should be correct.
3. The correct answer must exactly match one of the options.
4. Generate questions from different concepts and subtopics within the given topic.
5. Do not generate multiple questions testing the same concept.
6. Avoid repeating common beginner-level questions.
7. Include a balanced difficulty distribution:
   - 30% Beginner
   - 50% Intermediate
   - 20% Advanced

Before creating questions:
- Identify the major subtopics within the topic.
- Select different subtopics.
- Create one unique question per selected concept.

The questions should test understanding, not just memorization.

Return only the structured output.""")
        st.session_state["Q&AList"] = [
            q.model_dump()
            for q in response.questions
        ]



if "currentQuestion" not in st.session_state : 
	st.session_state["currentQuestion"] = 0
if "isExamCompleted" not in st.session_state : 
    st.session_state["isExamCompleted"] = False
if st.session_state["isExamCompleted"]:
    score = 0
    st.write("🎉 Exam Completed Successfully! Here are your results 📊")
    for index,obj in enumerate(st.session_state["Q&AList"]):
        st.write(str(index+1)+"). "+obj["question"])
        st.write("✅ Correct Answer: ",obj["actualAnswer"])
        userAnswer = obj["userAnswer"] if "userAnswer" in obj else "NA"
        st.write("📝 Your Answer: ",userAnswer)
        if obj["actualAnswer"] == userAnswer:
            st.success("🎉 Correct! Great job!")
            score += 1
        else:
            st.error("❌ Incorrect. Keep learning!")
    st.write(f"🏆 Final Score :{(score / len(st.session_state["Q&AList"])) * 100:.2f}%")
else : 
    st.progress((st.session_state["currentQuestion"] + 1) / len(st.session_state["Q&AList"]))
    st.caption(f"📌 Question {st.session_state["currentQuestion"] + 1} of {len(st.session_state["Q&AList"])}")
    with st.container(border=True):
        ans = st.radio(
            str(st.session_state["currentQuestion"] + 1) + ") " +
            st.session_state["Q&AList"][st.session_state["currentQuestion"]]["question"],
            st.session_state["Q&AList"][st.session_state["currentQuestion"]]["options"]
        )
        col1, col2, col3 = st.columns([1, 1, 1])
        if st.session_state["currentQuestion"] > -1 and st.session_state["currentQuestion"] < len(st.session_state["Q&AList"]):
            with col1:
                if st.session_state["currentQuestion"] != 0:
                    if st.button("⬅️ Previous", use_container_width=True):
                        st.session_state["Q&AList"][st.session_state["currentQuestion"]]["userAnswer"] = ans
                        st.session_state["currentQuestion"] -= 1
                        st.rerun()
            with col2:
                if st.session_state["currentQuestion"] != len(st.session_state["Q&AList"])-1:
                    if st.button("Next ➡️", use_container_width=True):
                        st.session_state["Q&AList"][st.session_state["currentQuestion"]]["userAnswer"] = ans
                        st.session_state["currentQuestion"] += 1
                        st.rerun()
            with col3:
                if st.button("🏁 Submit Exam", use_container_width=True):
                    st.session_state["Q&AList"][st.session_state["currentQuestion"]]["userAnswer"] = ans
                    st.session_state["isExamCompleted"] = True
                    st.rerun()
