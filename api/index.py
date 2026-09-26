import os
import json
from flask import Flask, render_template_string, redirect, url_for, send_from_directory, request, jsonify

app = Flask(__name__)

# Vercel ephemeral storage directories
UPLOAD_FOLDER = '/tmp'
CHAT_FILE = '/tmp/chat.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper to load and save chat messages
def load_messages():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_message(username, text):
    messages = load_messages()
    messages.append({"username": username, "text": text})
    # Keep only the last 50 messages to prevent bloat
    if len(messages) > 50:
        messages = messages[-50:]
    with open(CHAT_FILE, 'w') as f:
        json.dump(messages, f)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File Share & Chat App</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 700px; margin: 30px auto; padding: 20px; background: #f4f4f7; color: #111; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
        h2 { color: #0070f3; margin-top: 0; font-size: 1.2rem; }
        input[type="file"], input[type="text"], textarea { width: 100%; box-sizing: border-box; margin: 10px 0; padding: 8px; border: 1px solid #ddd; border-radius: 6px; }
        button { background: #0070f3; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-weight: 600; cursor: pointer; }
        button:hover { background: #0051a2; }
        ul { padding-left: 20px; max-height: 150px; overflow-y: auto; }
        li { margin: 6px 0; }
        a { color: #0070f3; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .chat-box { height: 180px; border: 1px solid #eee; border-radius: 6px; overflow-y: scroll; padding: 10px; background: #fafafa; margin-bottom: 10px; font-size: 14px; }
        .chat-msg { margin-bottom: 6px; }
        .chat-msg strong { color: #0070f3; }
        .note { font-size: 11px; color: #666; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="grid">
        <!-- File Sharing Section -->
        <div>
            <div class="card">
                <h2>📤 Upload File</h2>
                <form method="POST" enctype="multipart/form-data" action="/upload">
                    <input type="file" name="file" required>
                    <button type="submit">Upload</button>
                </form>
            </div>
            
            <div class="card">
                <h2>📥 Files</h2>
                {% if files %}
                    <ul>
                        {% for file in files %}
                            <li><a href="/download/{{ file }}" target="_blank">{{ file }}</a></li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p style="font-size: 13px; color: #777;">No files uploaded.</p>
                {% endif %}
            </div>
        </div>

        <!-- Live Chat Section -->
        <div>
            <div class="card">
                <h2>💬 Room Chat</h2>
                <div class="chat-box" id="chatBox">
                    Loading messages...
                </div>
                <form id="chatForm">
                    <input type="text" id="username" placeholder="Your Name" required style="margin-bottom: 5px;">
                    <input type="text" id="messageText" placeholder="Type a message..." required style="margin-bottom: 8px;">
                    <button type="submit" style="width: 100%;">Send Message</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        async function fetchMessages() {
            try {
                let res = await fetch('/api/messages');
                let messages = await res.json();
                let chatBox = document.getElementById('chatBox');
                chatBox.innerHTML = messages.map(m => `<div class="chat-msg"><strong>${escapeHtml(m.username)}:</strong> ${escapeHtml(m.text)}</div>`).join('');
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (e) {
                console.error("Failed to load chat", e);
            }
        }

        function escapeHtml(text) {
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        document.getElementById('chatForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            let username = document.getElementById('username').value;
            let text = document.getElementById('messageText').value;

            await fetch('/api/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, text })
            });

            document.getElementById('messageText').value = '';
            fetchMessages();
        });

        // Poll for new messages every 3 seconds
        setInterval(fetchMessages, 3000);
        fetchMessages();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    # Filter out internal tracking files like chat.json from file-sharing list
    files = [f for f in files if f != 'chat.json']
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# Chat API endpoints
@app.route('/api/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        data = request.get_json()
        if data and 'username' in data and 'text' in data:
            save_message(data['username'], data['text'])
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "error"}), 400
    
    return jsonify(load_messages())

if __name__ == '__main__':
    app.run(debug=True)