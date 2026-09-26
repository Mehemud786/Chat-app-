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

@app.route('/', methods=['GET', 'POST'])
@app.route('/api', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file_id = str(uuid.uuid4())[:8]
        file_storage[file_id] = {'title': title, 'content': content}
        return redirect(url_for('index'))
    return render_template_string(HTML_TEMPLATE, files=file_storage)

@app.route('/file/<file_id>')
@app.route('/api/file/<file_id>')
def view_file(file_id):
    file_data = file_storage.get(file_id)
    if not file_data:
        return "File not found", 404
    return render_template_string(VIEW_TEMPLATE, file=file_data)