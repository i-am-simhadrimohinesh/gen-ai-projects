# 1. Imports
import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage
from uuid import uuid4
from backend import chatworkflow,checkpointer,delete_thread_by_id

# 2. Main Page UI
st.set_page_config(
    page_title="AI Chat Application",
    page_icon="🤖",
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
def get_thread_title(thread_id:str) -> str:
    state = chatworkflow.get_state(
            config=get_config(thread_id)
        )
    if state.values:
        return state.values.get("title", "New Chat")
    return "New Chat"


# 4. Initialise the session_state
if "thread_list" not in st.session_state:
    thread_set = set() 
    for obj in checkpointer.list(None):
        thread_set.add(obj.config["configurable"]["thread_id"])
        # if thread_id not in thread_list: --> this will check multiple times for each thread lookups n number of threads
    st.session_state["thread_list"] = list(thread_set)

# Initialise the new chat by default
if "current_thread" not in st.session_state:
    thread_id = generate_thread_id()
    st.session_state["current_thread"] = thread_id
    st.session_state["thread_list"].append(thread_id)


current_thread = st.session_state["current_thread"] 

# 5. Side bar UI
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("New Chat"):
    thread_id = generate_thread_id()
    st.session_state["current_thread"] = thread_id
    st.session_state["thread_list"].append(thread_id)
    st.rerun()
st.sidebar.header("My Conversations")
for thread_id in st.session_state["thread_list"][::-1]:
    col1, col2 = st.sidebar.columns([4, 1])
    title = get_thread_title(thread_id)
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
            delete_thread_by_id(thread_id)
            # If the deleted thread is currently open,create/select another thread
            if thread_id == current_thread:
                if st.session_state["thread_list"]:
                    st.session_state["current_thread"] = st.session_state["thread_list"][-1]
                else:
                    new_thread_id = generate_thread_id()
                    st.session_state["thread_list"].append(new_thread_id)
                    st.session_state["current_thread"] = new_thread_id
            st.rerun()

# 6. Prepare current thread Data

thread_config = get_config(current_thread)
with st.spinner("Loading conversation..."):
    state = chatworkflow.get_state(config = thread_config)
history = (
    state.values.get("history", [])
    if state.values
    else []
)
# 7 . Display Chat History
if not history:
    st.info("Start a new conversation by typing a message below.")
else: 
    for message in history:
            if isinstance(message,HumanMessage):
                st.chat_message("user").write(message.content)
            elif isinstance(message,AIMessage):
                st.chat_message("ai").write(message.content)
    
# 8. Handle New Messages
if user_query:= st.chat_input("Type your message here"):
    st.chat_message("user").write(user_query)
    try:
        with st.chat_message("ai"):
            st.write_stream(
                message_chunk.content[0]["text"]
                for message_chunk, metadata in chatworkflow.stream(
                    {"userQuery": user_query},
                    config=thread_config,
                    stream_mode="messages"
                )
                if isinstance(message_chunk.content, list)
                for chunk in message_chunk.content
                if isinstance(chunk, dict) and chunk.get("type") == "text"
            )
    except Exception as e:
        print(e)
        st.error("Failed to generate a response. Please try again.")
    