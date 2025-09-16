import os
import logging
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, ToolMessage
from src.llm.model import get_gemini_model
from src.tools.search_tools import tavily_search
from src.tools.date_tools import get_current_date, get_current_time
from src.tools.weather import get_weather
from src.tools.crypto_markets import get_crypto_price, get_crypto_details, get_trending_cryptos, search_crypto_coins, get_crypto_market_overview, get_top_cryptos
from .utils.prompts import CHAT_PROMPT

class State(TypedDict):
    messages: Annotated[list, add_messages]
    topic: Literal["general", "news", "finance"]

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
        self.llm_with_tools = self.llm.bind_tools([
            tavily_search,
            get_current_date,
            get_current_time,
            get_weather,
            get_crypto_price,
            get_crypto_details,
            get_trending_cryptos,
            search_crypto_coins,
            get_crypto_market_overview,
            get_top_cryptos])
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
        chain = CHAT_PROMPT | self.llm_with_tools
        result = await chain.ainvoke({"messages": state["messages"]})
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

        tool_map = {
            "get_date": get_current_date,
            "get_time": get_current_time,
            "tavily_search": tavily_search,
            "get_weather": get_weather,
            "get_crypto_price": get_crypto_price,
            "get_crypto_details": get_crypto_details,
            "get_trending_cryptos": get_trending_cryptos,
            "search_crypto_coins": search_crypto_coins,
            "get_crypto_market_overview": get_crypto_market_overview,
            "get_top_cryptos": get_top_cryptos
        }

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_id = tool_call["id"]
            tool_args = tool_call["args"]

            if tool_name not in tool_map:
                logging.warning(f"Unknown tool: {tool_name}")
                continue

            logging.info(f"Calling {tool_name} tool")

            if tool_name == "tavily_search":
                tool_args = {
                    **tool_args,
                    "topic": state["topic"],
                    "max_results": 20 if state["topic"] == "news" else 15,
                }

            result = await tool_map[tool_name].ainvoke(tool_args)

            tool_message = ToolMessage(
                name=tool_name,
                content=str(result),
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