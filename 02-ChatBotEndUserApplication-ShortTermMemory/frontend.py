import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage
from uuid import uuid4
from backend import chatworkflow

# Main UI
st.title("Welcome to AI Chat Application")

# Utility Functions
def generate_thread_id():
    return str(uuid4())

# Initialise the session state variables

if 'threadList' not in st.session_state:
    st.session_state['threadList'] = []
if 'currentThread' not in st.session_state:
    thread_id = generate_thread_id()
    st.session_state['currentThread'] = thread_id
    st.session_state['threadList'].append(thread_id)

state = chatworkflow.get_state(config = {
"configurable": {
    "thread_id" : st.session_state['currentThread']
}})

if state.values:
    st.session_state['currentThreadHistory'] = state.values.get("history",[])
else : 
    st.session_state['currentThreadHistory'] = []

for message in st.session_state['currentThreadHistory']:
    if isinstance(message,HumanMessage):
        st.chat_message("user").text(message.content)
    else:
        st.chat_message("ai").text(message.content)

# Side bar UI
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("New Chat"):
    thread_id = generate_thread_id()
    st.session_state['currentThread'] = thread_id
    st.session_state['threadList'].append(thread_id)
    st.rerun()
st.sidebar.header("My Conversations")
for thread in st.session_state['threadList'][::-1]:
    if st.sidebar.button(str(thread)):
        st.session_state['currentThread'] = str(thread)
        st.rerun()

# Logic for Chat
config = {
    "configurable": {
        "thread_id" : st.session_state['currentThread']
    }
}

userQuery = st.chat_input("Type your message here")

if userQuery:
    st.chat_message("user").text(userQuery)
    res = chatworkflow.invoke({
            'userQuery':userQuery
            },
        config={
            "configurable":{
                "thread_id":st.session_state['currentThread']
                }
            })['result']
    st.chat_message("ai").text(res)