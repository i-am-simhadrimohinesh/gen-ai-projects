# 1. Imports
import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.types import Command
from uuid import uuid4
from backend import chatworkflow,checkpointer,delete_thread_by_id,load_pdf

# 2. Main Page UI
st.set_page_config(
    page_title="AI Chat Application",
    # page_icon="🤖",
    layout="wide",
)
st.title("Welcome to AI Chat Application")

# 3. Utility & Helper Functions
def generate_thread_id() -> str:
    return str(uuid4())

def get_config(thread_id:str) -> dict:
    return {
        "configurable": {
            "thread_id" : thread_id
        }           
    }

# 4. Initialise the session_state
if "thread_list" not in st.session_state:
    thread_set = set()
    thread_titles = {}
    for obj in checkpointer.list(None):
        thread_id = obj.config["configurable"]["thread_id"]
        if thread_id not in thread_set:
            thread_set.add(thread_id)
            channel_values = obj.checkpoint.get("channel_values", {})
            title = channel_values.get("title", "New Chat")
            thread_titles[thread_id] = title
    st.session_state["thread_list"] = list(thread_set)
    st.session_state["thread_titles"] = thread_titles

# Initialise the new chat by default
if "current_thread" not in st.session_state:
    thread_id = generate_thread_id()
    st.session_state["current_thread"] = thread_id
    st.session_state["thread_list"].append(thread_id)
    st.session_state["thread_titles"][thread_id] = "New Chat"

current_thread = st.session_state["current_thread"] 

# 5. Side bar UI
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("New Chat"):
    thread_id = generate_thread_id()
    st.session_state["current_thread"] = thread_id
    st.session_state["thread_list"].append(thread_id)
    st.session_state["thread_titles"][thread_id] = "New Chat"
    st.rerun()

if "uploaded_file_name" not in st.session_state:
    st.session_state["uploaded_file_name"] = None
uploaded_file = st.sidebar.file_uploader(
    "📄 Upload PDF",
    type=["pdf"]
)

if uploaded_file:
    if uploaded_file.name != st.session_state["uploaded_file_name"]:
        load_pdf(uploaded_file)
        st.session_state["uploaded_file_name"] = uploaded_file.name

st.sidebar.header("My Conversations")
for thread_id in st.session_state["thread_list"][::-1]:
    col1, col2 = st.sidebar.columns([4, 1])
    title = st.session_state["thread_titles"].get(thread_id, "New Chat")
    label = (
        f"👉 {title}"
        if thread_id == current_thread
        else title
    )
    with col1:
        if st.button(label, key=f"thread_{thread_id}", use_container_width=True):
            st.session_state["current_thread"] = thread_id
            st.rerun()
    with col2:
        if st.button("🗑️", key=f"delete_{thread_id}", use_container_width=True):
            st.session_state["thread_list"].remove(thread_id)
            st.session_state["thread_titles"].pop(thread_id, None)
            delete_thread_by_id(thread_id)
            # If the deleted thread is currently open,create/select another thread
            if thread_id == current_thread:
                if st.session_state["thread_list"]:
                    st.session_state["current_thread"] = st.session_state["thread_list"][-1]
                else:
                    new_thread_id = generate_thread_id()
                    st.session_state["thread_list"].append(new_thread_id)
                    st.session_state["current_thread"] = new_thread_id
                    st.session_state["thread_titles"][new_thread_id] = "New Chat"
            st.rerun()

# 6. Prepare current thread Data
thread_config = get_config(current_thread)
with st.spinner("Loading conversation..."):
    state = chatworkflow.get_state(config = thread_config)
st.session_state["thread_titles"][current_thread] = (
    state.values.get("title", "New Chat")
)
messages = (
    state.values.get("messages", [])
    if state.values
    else []
)
def get_interrupt(state):
    for task in state.tasks:
        if task.interrupts:
            return task.interrupts[0]

    return None
pending_interrupt = get_interrupt(state)

# 7 . Display Chat messages
if not messages:
    st.info("Start a new conversation by typing a message below.")
else: 
    for message in messages:
            if isinstance(message,HumanMessage):
                st.chat_message("user").write(message.content)
            elif isinstance(message,AIMessage):
                if message.content:
                    st.chat_message("ai").write(message.content[0]['text'])

if pending_interrupt:
    interrupt_data = pending_interrupt.value
    with st.chat_message("ai"):
        st.warning("⚠️ Human approval required")
        st.write(f"**Reason:** {interrupt_data['reason']}")
        st.write(f"**Question:** {interrupt_data['question']}")
        st.caption(interrupt_data["instruction"])
        col1, col2 = st.columns(2)
        with col1:
            approve = st.button("✅ Approve",use_container_width=True)
        with col2:
            reject = st.button("❌ Reject",use_container_width=True)
    if approve:
        with st.spinner("Generating..."):
            with st.chat_message("ai"):
                for message_chunk, metadata in chatworkflow.stream(
                    Command(resume={"result": "approved"}),
                    config=thread_config,
                    stream_mode="messages"
                ):
                    if isinstance(message_chunk.content, list):
                        for chunk in message_chunk.content:
                            if (
                                isinstance(chunk, dict)
                                and chunk.get("type") == "text"
                                and chunk.get("text")
                            ):
                                st.write(chunk["text"])
        st.rerun()
    if reject:
        with st.spinner("Generating..."):
            with st.chat_message("ai"):
                for message_chunk, metadata in chatworkflow.stream(
                    Command(resume={"result": "rejected"}),
                    config=thread_config,
                    stream_mode="messages"
                ):
                    if isinstance(message_chunk.content, list):
                        for chunk in message_chunk.content:
                            if (
                                isinstance(chunk, dict)
                                and chunk.get("type") == "text"
                                and chunk.get("text")
                            ):
                                st.write(chunk["text"])
        st.rerun()
if not pending_interrupt:
    # 8. Handle New Messages
    if user_query:= st.chat_input("Type your message here"):
        st.chat_message("user").write(user_query)
        try:      
            with st.spinner("Generating..."):
                st.write_stream(
                    chunk["text"]
                    for message_chunk, metadata in chatworkflow.stream(
                        {"messages": [HumanMessage(user_query)]},
                        config=thread_config,
                        stream_mode="messages"
                    )
                    if isinstance(message_chunk.content, list)
                    for chunk in message_chunk.content
                    if isinstance(chunk, dict) and chunk.get("type") == "text"
                )
            st.rerun()
        except Exception as e:
            print(e)
            st.error("Failed to generate a response. Please try again.")   
