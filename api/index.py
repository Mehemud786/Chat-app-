import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# MongoDB Atlas connection
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["chatapp_db"]

users_collection = db["users"]
messages_collection = db["messages"]

class UserLogin(BaseModel.model_config = {**BaseModel.model_config}, *, username: str):
    username: str

class Message(BaseModel):
    user: str
    text: str

@app.post("/api/login")
def login_user(data: UserLogin):
    username = data.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    
    # Check if user exists in MongoDB, otherwise create them
    existing_user = users_collection.find_one({"username": username})
    if not existing_user:
        users_collection.insert_one({"username": username})
        
    return {"status": "success", "username": username}

@app.get("/api/messages")
def get_messages():
    try:
        messages = list(messages_collection.find({}, {"_id": 0}).sort("_id", 1).limit(50))
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages")
def post_message(msg: Message):
    try:
        message_data = {"user": msg.user, "text": msg.text}
        messages_collection.insert_one(message_data)
        return {"status": "success", "message": message_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))