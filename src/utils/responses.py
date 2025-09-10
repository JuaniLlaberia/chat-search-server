import logging
import json
import ast
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from uuid import uuid4
from typing import Optional

async def generate_chat_responses(graph: StateGraph, message: str, checkpoint_id: Optional[str] = None):
    """
    Generate streaming chat responses

    Args:
        graph (StateGraph): Orchestrator graph
        message (str): Message
        checkpoint_id (str | None): Checkpoint id for langgraph
    """
    try:
        if checkpoint_id is None:
            # Create unique id to find memory
            checkpoint_id = str(uuid4())

            yield f"data: {json.dumps({'type': 'checkpoint', 'checkpoint_id': checkpoint_id})}\n\n"

        config = {"configurable": {"thread_id": checkpoint_id}}

        input_data = {"messages": [HumanMessage(content=message.strip())]}

        sent_content = set()
        total_content = ""

        async for event in graph.astream_events(input_data, config=config, version="v2"):
            try:
                event_type = event.get("event", "")
                event_name = event.get("name", "")
                event_data = event.get("data", {})

                logging.info(f"Event: {event_type} | Name: {event_name}")

                # Handle tool_node
                if event_name == "tool_node" and event_type in ["on_chain_stream", "on_chain_end"]:
                    chunk = event_data.get("chunk", {})
                    messages = chunk.get("messages", [])

                    if messages:
                        first_message = messages[0]

                        # Web search tool
                        if hasattr(first_message, 'name') and first_message.name == "duckduckgo_results_json":
                            tool_output_string = first_message.content

                            try:
                                # Parse the string into a dictionary.
                                results = ast.literal_eval(tool_output_string)
                                urls = [item["link"] for item in results if isinstance(item, dict) and "link" in item]

                                if urls:
                                    yield f"data: {json.dumps({'type': 'search_results', 'urls': urls})}\n\n"

                            except (ValueError, SyntaxError, AttributeError) as e:
                                logging.error(f"Error parsing tool output: {e}")
                # Handle streaming chain
                elif event_type == "on_chain_stream":
                    chunk = event_data.get("chunk", {})

                    if isinstance(chunk, dict) and "messages" in chunk:
                        for msg in chunk["messages"]:
                            if hasattr(msg, "content") and msg.content:
                                content = msg.content
                                if content and content not in sent_content:
                                    sent_content.add(content)
                                    total_content += content
                                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"

                    elif hasattr(chunk, "content") and chunk.content:
                        content = chunk.content
                        if content and content not in sent_content:
                            sent_content.add(content)
                            total_content += content
                            yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"

            except Exception as e:
                logging.error(f"Error processing event {event_type}: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    except Exception as e:
        logging.error(f"Error in generate_chat_responses: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': f'Stream error: {str(e)}'})}\n\n"