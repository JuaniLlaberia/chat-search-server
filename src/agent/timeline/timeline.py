import logging
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from .models.output import TimelineEvent, TimelineOutput, EvaluateTimelineOutput
from .utils.prompts import TIMELINE_PROMPT, EVALUATE_TIMELINE_PROMPT

class State(TypedDict):
    events: list[TimelineEvent]
    score: float
    improvements: str | None

    user_query: str
    search_info: list

class Timeline:
    """
    Timeline generator agent
    """
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initializes a new instance of the Timeline workflow

        Args:
            llm (ChatGoogleGenerativeAI): Instance of google gerative model (gemini)
        """
        if llm is None:
            raise ValueError("LLM instance must be provided")
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build timeline agent graph
        """
        graph = StateGraph(State)

        graph.add_node("generation_node", self._generate_timeline)
        graph.add_node("evaluation_node", self._evaluate_timeline)

        graph.set_entry_point("generation_node")
        graph.add_conditional_edges(
            "evaluation_node",
            self._validate_timeline,
            {
                "continue": "generation_node",
                "end": END
            }
        )

        return graph.compile()

    async def _generate_timeline(self, state: State):
        """
        Generates timeline using LLM with structured output
        """
        structured_llm = self.llm.with_structured_output(TimelineOutput)
        chain = TIMELINE_PROMPT | structured_llm

        response = await chain.ainvoke({
            "user_query": state["user_query"],
            "search_info": state["search_info"],
            "improvements": state["improvements"],
        })

        if isinstance(response, TimelineOutput):
            timeline_data = {"events": response.events}
        else:
            response_data = response.model_dump()
            timeline_data = {"events": response_data.get("events", [])}

        return {
            "events": timeline_data["events"]
        }

    async def _evaluate_timeline(self, state: State):
        """
        Evaluates that the timeline was properly generated using certain parameters and generates a score
        """
        structured_llm = self.llm.with_structured_output(EvaluateTimelineOutput)
        chain = EVALUATE_TIMELINE_PROMPT | structured_llm

        response = await chain.ainvoke({
            "events": state["events"],
        })

        if isinstance(response, EvaluateTimelineOutput):
            evaluation_data = {
                "score": response.score,
                "improvements": response.improvements,
            }
        else:
            response_data = response.model_dump()
            evaluation_data = {
                "score": response_data.get("score", []),
                "improvements": response_data.get("improvements", [])
            }

        return {**evaluation_data}

    def _validate_timeline(self, state: State):
        """
        Validator method to check score and decide if we should re-iterate or end process
        """
        return "end" if state["score"] >= 0.8 else "continue"

    async def run(self, user_query: str, search_info: list):
        """
        Run timeline agent
        """
        initial_state = State(
            events=[],
            score=0,
            improvements="",
            user_query=user_query,
            search_info=search_info
        )

        logging.info("Running timeline agent")
        results = await self.graph.ainvoke(initial_state)

        return results["events"]
