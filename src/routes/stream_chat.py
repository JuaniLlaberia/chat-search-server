import os
import logging
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from src.utils.responses import generate_chat_responses
from src.agent.chat.chat import Chat

chat_router = APIRouter()
graph_instance = Chat(model_name=os.getenv("MODEL_NAME", "gemini-2.5-flash")).graph

@chat_router.get("/chat_stream/{message}")
async def chat_stream(message: str, checkpoint_id: str | None = Query(None)):
    """
    Endpoint to stream chat responses
    """
    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")


    logging.info("Server-Sent Events (SSE) connection stablished")
    return StreamingResponse(
        generate_chat_responses(
            graph=graph_instance,
            message=message,
            checkpoint_id=checkpoint_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

