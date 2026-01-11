from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model(
    model="gpt-4.1-mini",
    model_provider="openai",
)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
    
def chatbot(state: State): 
    response = llm.invoke(state.get("messages"))
    return {"messages": [response]} 

def samplenode(state: State): 
    print("\n\nInside samplenode\n", state)
    return {"messages": ["Sample message appended"]}
    
graph_builder= StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("samplenode", samplenode)

graph_builder.add_edge(START,"chatbot")
graph_builder.add_edge("chatbot", "samplenode")
graph_builder.add_edge("samplenode",END)

graph= graph_builder.compile()

updated_state = graph.invoke(State({"messages": ["Hi, My name is siddharth"]}))
print("\n\nUpdated state: ", updated_state)

# (START) -> chatbot ->  samplenode -> (END)


# state = {messages: ["Hey there"]}
# node runs: chatbot(state: ["Hey there"]) -> ["Hi, This is a message from chatbot node"]
# state after node run: {messages: ["Hey there", "Hi, This is a message from chatbot node"]}

