from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict,Annotated
import sqlite3
import atexit

load_dotenv()

class ChatState(TypedDict):
    messages : Annotated[list,add_messages]
    title : str

model = ChatGoogleGenerativeAI(model='gemini-3.5-flash-lite')

# Create Tools
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(firstNumber:float , secondNumber:float,operation:str)->dict:
    """ Perform the mathematical addition operation for the given two numbers"""
    if  operation == "add":
        return {
            "firstNumber":firstNumber,
            "secondNumber":secondNumber,
            "operation":operation,
            "result":firstNumber + secondNumber
            }

tools = [search_tool,calculator]
model_with_tools = model.bind_tools(tools)

def llm_call(state):
    # Set title only once
    if not state.get("title"):
        title = state["messages"][-1].content[:30]
        if len(state["messages"][-1].content) > 30:
            title += "..."
        state["title"] = title
    response = model_with_tools.invoke(state["messages"])
    return {
        "messages" : [response],
        "title" : state["title"]
    }

tool_node = ToolNode(tools)

graph = StateGraph(ChatState)
graph.add_node('llmcall',llm_call)
graph.add_node('tools',tool_node)
graph.add_edge(START,'llmcall')
graph.add_conditional_edges('llmcall',tools_condition)
graph.add_edge('tools','llmcall')

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