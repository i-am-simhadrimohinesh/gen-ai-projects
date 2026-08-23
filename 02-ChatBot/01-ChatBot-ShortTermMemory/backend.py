from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage,AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict

load_dotenv()
class ChatState(TypedDict):
    userQuery : str
    result : str
    history : list

model = ChatGoogleGenerativeAI(model='gemini-3.5-flash-lite')
def llmcall(state):
    history = state.get("history",[])
    history.append(HumanMessage(state['userQuery']))
    response = model.invoke(history).content[0]['text']
    history.append(AIMessage(response))
    state['result'] = response
    state['history'] = history
    return state

graph = StateGraph(ChatState)
graph.add_node('llmcall',llmcall)
graph.add_edge(START,'llmcall')
graph.add_edge('llmcall',END)

checkpointer = InMemorySaver()
chatworkflow = graph.compile(checkpointer=checkpointer)

# res = chatworkflow.get_state({"configurable":{"thread_id":"user-111"}})
# print(res)