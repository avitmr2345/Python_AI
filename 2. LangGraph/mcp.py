from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import asyncio
from langchain.mcp import MCPAdapter

load_dotenv()  # Load environment variables from .env file

llm = ChatOpenAI(model="gpt-5")

# Structure config following the standardized mcpServers format
config = {
    "mcpServers": {
        "arith": {
            "command": "python3",
            "args": ["/Users/avish/Desktop/mcp-math-server/main.py"],
        },
        "expense": {"url": "https://splendid-gold-dingo.fastmcp.app/mcp"},
    }
}


# state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def build_graph(adapter: MCPAdapter):
    tools = adapter.list_tools()
    print("Discovered tools:", tools)
    llm_with_tools = llm.bind_tools(tools)

    # nodes
    async def chat_node(state: ChatState):
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    # defining graph and nodes
    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    # defining graph connections
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile()
    return chatbot


async def main():
    # 2. Open the adapter context manager here so connections persist during the run
    async with MCPAdapter(config) as adapter:

        # Build the graph inside the open context
        chatbot = build_graph(adapter)

        # Running the graph
        result = await chatbot.ainvoke(
            {
                "messages": [
                    HumanMessage(
                        content="Give me all my expenses for the month of Nov from 1 Nov to 30 Nov"
                    )
                ]
            }
        )
        print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
