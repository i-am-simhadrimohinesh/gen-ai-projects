from langgraph.graph import StateGraph,START,END
import sqlite3
import atexit
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage,AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict

load_dotenv()
class ChatState(TypedDict):
    userQuery : str
    result : str
    history : list
    title : str

model = ChatGoogleGenerativeAI(model='gemini-3.5-flash-lite')
def llm_call(state):
    history = state.get("history",[])
    history.append(HumanMessage(state['userQuery']))
    # Set title only once
    if not state.get("title"):
        title = state["userQuery"][:30]
        if len(state["userQuery"]) > 30:
            title += "..."
        state["title"] = title
    response = model.invoke(history).content[0]['text']
    history.append(AIMessage(response))
    state['result'] = response
    state['history'] = history
    return state

graph = StateGraph(ChatState)
graph.add_node('llmcall',llm_call)
graph.add_edge(START,'llmcall')
graph.add_edge('llmcall',END)

conn = sqlite3.connect(database="chatbot.db",check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

@atexit.register
def cleanup():
    conn.close()

def delete_thread_by_id(thread_id):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM writes WHERE thread_id = ?",
        (thread_id,)
    )
    cursor.execute(
        "DELETE FROM checkpoints WHERE thread_id = ?",
        (thread_id,)
    )
    conn.commit()
    cursor.close()
chatworkflow = graph.compile(checkpointer=checkpointer)
