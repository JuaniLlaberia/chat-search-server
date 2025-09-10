import logging
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.stream_chat import chat_router
from src.routes.helper import helper_router

load_dotenv()

logging.basicConfig(filemode="server.log", level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"]
)

app.include_router(chat_router)
app.include_router(helper_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)