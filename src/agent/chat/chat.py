import os
import logging
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, add_messages, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from src.llm.model import get_gemini_model
from src.tools.search_tools import tavily_search
from src.tools.date_tools import get_current_date, get_current_time
from src.tools.weather import get_weather
from src.tools.crypto_markets import get_crypto_price, get_crypto_details, get_trending_cryptos, search_crypto_coins, get_crypto_market_overview, get_top_cryptos
from src.agent.timeline.timeline import Timeline
from src.agent.timeline.models.output import TimelineEvent
from .utils.prompts import CHAT_PROMPT, FOLLOWUP_QUESTIONS_PROMPT, TIMELINE_CHAT_PROMPT
from .models.output import FollowupOutput

class State(TypedDict):
    messages: Annotated[list, add_messages]
    topic: Literal["general", "news", "finance"]
    followup_questions: list[str]
    mode: Literal["informative", "timeline"]
    events: list[TimelineEvent]
    initial_response_generated: bool

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
        self.timeline_agent = Timeline(llm=self.llm)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build chat agent graph
        """
        graph = StateGraph(State)

        # Add nodes
        graph.add_node("initial_llm_node", self._initial_llm_node)
        graph.add_node("tool_node", self._tool_node)
        graph.add_node("followup_node", self._followup_node)
        graph.add_node("timeline_node", self._timeline_node)
        graph.add_node("final_llm_node", self._final_llm_node)

        # Add edges
        graph.add_edge(START, "initial_llm_node")

        # Main content flow
        graph.add_conditional_edges(
            "initial_llm_node",
            self._tools_router,
            {
                "tools": "tool_node",
                "timeline": "timeline_node",
                "final": "final_llm_node",
                "end": END
            }
        )

        # Parallel followup flow
        graph.add_edge("initial_llm_node", "followup_node")

        # After tools, decide next step based on mode
        graph.add_conditional_edges(
            "tool_node",
            self._after_tools_router,
            {
                "timeline": "timeline_node",
                "final": "final_llm_node"
            }
        )

        graph.add_edge("timeline_node", END)
        graph.add_edge("final_llm_node", END)
        graph.add_edge("followup_node", END)

        return graph.compile(checkpointer=self.memory)

    async def _initial_llm_node(self, state: State) -> dict[str, any]:
        """
        Initial LLM call that generates the first response and determines next steps
        """
        if state.get("mode") == "timeline":
            chain = TIMELINE_CHAT_PROMPT | self.llm_with_tools
        else:
            chain = CHAT_PROMPT | self.llm_with_tools

        result = await chain.ainvoke({"messages": state["messages"]})

        return {
            "messages": [result],
            "initial_response_generated": True
        }

    async def _tool_node(self, state: State) -> dict[str, list]:
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
                    "max_results": 25 if state.get("mode") == "timeline" else (20 if state["topic"] == "news" else 15),
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

    async def _final_llm_node(self, state: State) -> dict[str, list[BaseMessage]]:
        """
        Final LLM call after tools have been executed (for informative mode)
        """
        if state.get("mode") == "timeline":
            return {"messages": []}

        chain = CHAT_PROMPT | self.llm_with_tools
        result = await chain.ainvoke({"messages": state["messages"]})
        return {
            "messages": [result]
        }

    async def _after_tools_router(self, state: State) -> Literal["timeline", "final"]:
        """
        Router to decide what to do after tools have been executed
        """
        if state["mode"] == "timeline":
            return "timeline"
        else:
            return "final"

    async def _tools_router(self, state: State) -> Literal["tools", "timeline", "final", "end"]:
        """
        Node to decide if we need to use tools and route
        """
        last_message = state["messages"][-1]

        if(hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0):
            return "tools"
        elif state["mode"] == "timeline":
            return "timeline"
        elif state.get("mode") == "informative":
            return "final"
        else:
            return "end"

    async def _followup_node(self, state: State) -> dict[str, any]:
        """
        Node to generate follow-up questions based on user query (runs in parallel)
        """
        # Find the original user message
        user_message = None
        for message in state["messages"][::-1]:
            if isinstance(message, HumanMessage):
                user_message = message
                break

        if not user_message:
            return {"followup_questions": []}

        structured_llm = self.llm.with_structured_output(FollowupOutput)
        chain = FOLLOWUP_QUESTIONS_PROMPT | structured_llm

        response = await chain.ainvoke({
            "user_query": user_message.content
        })

        if isinstance(response, FollowupOutput):
            followup_data = {"questions": response.questions}
        else:
            response_data = response.model_dump()
            followup_data = {"questions": response_data.get("questions", [])}

        return {
            "followup_questions": followup_data["questions"]
        }

    async def _timeline_node(self, state: State) -> dict[str, any]:
        """
        Run timeline sub-agent
        """
        try:
            user_query, search_info = self._extract_timeline_data(state)

            if not user_query:
                logging.warning("No user query found for timeline generation")
                return {
                    "events": []
                }

            if not search_info:
                logging.warning("No search information found for timeline generation")
                return {
                    "events": []
                }

            # Run timeline agent
            timeline_events = await self.timeline_agent.run(
                user_query=user_query,
                search_info=search_info
            )

            return {"events": timeline_events}

        except Exception as e:
            logging.error(f"Error in timeline generation: {str(e)}")
            return {
                "events": []
            }

    def _extract_timeline_data(self, state: State) -> tuple[str, list]:
        """
        Extract user query and search information from messages for timeline generation

        Args:
            state: Current state containing messages

        Returns:
            tuple: (user_query, search_info)
        """
        user_query = ""
        search_info = []

        for message in state["messages"][::-1]:
            if isinstance(message, HumanMessage):
                user_query = message.content
                break

        for message in state["messages"]:
            if isinstance(message, ToolMessage) and message.name == "tavily_search":
                search_info.append(message.content)

        return user_query, search_info