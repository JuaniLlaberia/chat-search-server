import os
import logging
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, ToolMessage
from src.llm.model import get_gemini_model
from src.tools.search_tools import tavily_search
from src.tools.date_tools import get_current_date

class State(TypedDict):
    messages: Annotated[list, add_messages]

class Chat:
    """
    Chat agent/workflow
    """
    def __init__(self, model_name: str):
        """
        Initializes a new instance of Chat class

        Args:
            model_name (str): Name of the Google LLM
        """
        self.llm = get_gemini_model(
            model_name=model_name,
            api_key=os.getenv("GOOGLE_API_KEY", ""),
            temperature=0.05,
            top_p=0.3,
            top_k=10
        )
        self.llm_with_tools = self.llm.bind_tools([tavily_search, get_current_date])
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build chat agent graph
        """
        graph = StateGraph(State)

        # Add nodes
        graph.add_node("llm_node", self._llm_node)
        graph.add_node("tool_node", self._tool_node)

        # Add edges
        graph.set_entry_point("llm_node")
        graph.add_conditional_edges(
            "llm_node",
            self._tools_router,
            {
                "tools": "tool_node",
                "end": END
            }
        )
        graph.add_edge("tool_node", "llm_node")

        return graph.compile(checkpointer=self.memory)

    async def _llm_node(self, state: State) -> dict[str, list[BaseMessage]]:
        """
        Node that calls the llm with tools
        """
        result = await self.llm_with_tools.ainvoke(state["messages"])
        return {
            "messages": [result]
        }

    async def _tool_node(self, state: State):
        """
        Node that handles tool calls from the LLM
        """
        # Get tool calls from the last message
        tool_calls = state["messages"][-1].tool_calls
        # Initialize list to store tools messages
        tool_messages = []

        if not tool_calls:
            return {
                "messages": tool_messages
            }

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            if tool_name == "get_date":
                logging.info("Calling get_date tool")
                date = await get_current_date.ainvoke(tool_args)

                tool_message = ToolMessage(
                    name=tool_name,
                    content=str(date),
                    tool_call_id=tool_id
                )
                tool_messages.append(tool_message)

            elif tool_name == "tavily_search":
                logging.info("Calling tavily_search tool")
                search_results = await tavily_search.ainvoke(tool_args)

                tool_message = ToolMessage(
                    name=tool_name,
                    content=str(search_results),
                    tool_call_id=tool_id
                )
                tool_messages.append(tool_message)


        return {
            "messages": tool_messages
        }


    async def _tools_router(self, state: State) -> Literal["tools", "end"]:
        """
        Node to decide if we need to use tools and route
        """
        last_message = state["messages"][-1]

        if(hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0):
            return "tools"
        else:
            return "end"