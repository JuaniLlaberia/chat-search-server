from fastapi.testclient import TestClient
from src.routes.stream_chat import chat_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(chat_router)

def test_chat_stream():
    client = TestClient(app)
    response = client.get("/chat_stream/Hello")
    assert response.status_code == 200
