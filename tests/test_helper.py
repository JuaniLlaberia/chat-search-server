from fastapi.testclient import TestClient
from src.routes.helper import helper_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(helper_router)

def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200

def test_tools_endpoint():
    client = TestClient(app)
    response = client.get("/debug/tools")
    assert response.status_code == 200