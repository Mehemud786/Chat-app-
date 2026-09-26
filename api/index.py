from flask import Flask, render_template_string, request, redirect, url_for
import uuid

app = Flask(__name__)

# In-memory storage for files/snippets (Note: resets on serverless cold starts)
file_storage = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Python File/Text Sharer on Vercel</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #f4f4f9; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        input[type="text"], textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { background: #0070f3; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0051cc; }
        pre { background: #eee; padding: 10px; border-radius: 4px; overflow-x: auto; }
        .link { word-break: break-all; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🚀 Python Share App on Vercel</h2>
        <form method="POST" action="/api">
            <label>Title:</label>
            <input type="text" name="title" required placeholder="e.g., Notes.txt">
            <label>Content / Text Data:</label>
            <textarea name="content" rows="5" required placeholder="Type or paste your content here..."></textarea>
            <button type="submit">Upload / Share</button>
        </form>
    </div>

    <div class="card">
        <h3>📂 Shared Files Index</h3>
        <ul>
            {% for file_id, data in files.items() %}
                <li>
                    <strong>{{ data.title }}</strong> - 
                    <a href="/api/file/{{ file_id }}">View</a>
                </li>
            {% else %}
                <p>No files shared yet.</p>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

VIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ file.title }}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #f4f4f9; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        a { color: #0070f3; text-decoration: none; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📄 {{ file.title }}</h2>
        <pre>{{ file.content }}</pre>
        <br>
        <a href="/api">← Back to Home</a>
    </div>
</body>
</html>
"""

@app.route('/api', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        file_id = str(uuid.uuid4())[:8]
        file_storage[file_id] = {'title': title, 'content': content}
        return redirect(url_for('index'))
    return render_template_string(HTML_TEMPLATE, files=file_storage)

@app.route('/api/file/<file_id>')
def view_file(file_id):
    file_data = file_storage.get(file_id)
    if not file_data:
        return "File not found", 404
    return render_template_string(VIEW_TEMPLATE, file=file_data)