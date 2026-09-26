from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    username: str
    message: str

# In-memory store for demonstration (Note: Serverless instances can scale/isolate, 
# use Redis/Supabase for production multi-instance deployments)
MESSAGE_HISTORY = []

@app.get("/api/messages")
def get_messages():
    return {"messages": MESSAGE_HISTORY}

@app.post("/api/send")
def send_message(chat: ChatMessage):
    data = {"username": chat.username, "message": chat.message}
    MESSAGE_HISTORY.append(data)
    # Keep only last 50 messages
    if len(MESSAGE_HISTORY) > 50:
        MESSAGE_HISTORY.pop(0)
    return {"status": "success", "data": data}