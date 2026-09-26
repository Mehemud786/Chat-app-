import os
from flask import Flask, render_template_string, redirect, url_for, send_from_directory, request

app = Flask(__name__)

# Vercel allows writing only to the /tmp directory
UPLOAD_FOLDER = '/tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Python File Sharing App on Vercel</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #f9f9fb; color: #111; }
        .card { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; }
        h2 { color: #0070f3; margin-top: 0; }
        input[type="file"] { margin: 15px 0; display: block; }
        button { background: #0070f3; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; }
        button:hover { background: #0051a2; }
        ul { padding-left: 20px; }
        li { margin: 10px 0; }
        a { color: #0070f3; text-decoration: none; font-weight: 500; }
        a:hover { text-decoration: underline; }
        .note { font-size: 12px; color: #666; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📤 Upload File</h2>
        <form method="POST" enctype="multipart/form-data" action="/upload">
            <input type="file" name="file" required>
            <button type="submit">Upload to Cloud</button>
        </form>
    </div>
    
    <div class="card">
        <h2>📥 Available Files</h2>
        {% if files %}
            <ul>
                {% for file in files %}
                    <li><a href="/download/{{ file }}" target="_blank">{{ file }}</a></li>
                {% endfor %}
            </ul>
        {% else %}
            <p>No files uploaded yet.</p>
        {% endif %}
        <p class="note">Note: Files are stored temporarily in serverless ephemeral /tmp storage and may clear out between container restarts.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
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

if __name__ == '__main__':
    app.run(debug=True)