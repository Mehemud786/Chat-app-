from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

# Temporary in-memory message store 
# (Note: For permanent storage across serverless reboots, connect a database like KV or Supabase later)
ROOMS = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rooms/join', methods=['POST'])
def join_room():
    data = request.json or {}
    room_code = str(data.get('room_code', '')).strip()
    
    # Validate strict 4-digit numeric code
    if not room_code or len(room_code) != 4 or not room_code.isdigit():
        return jsonify({"error": "Invalid 4-digit room code"}), 400
    
    # Automatically initialize room if it doesn't exist yet
    if room_code not in ROOMS:
        ROOMS[room_code] = []
        
    return jsonify({"success": True, "room_code": room_code})

@app.route('/api/rooms/<room_code>/messages', methods=['GET', 'POST'])
def handle_messages(room_code):
    if room_code not in ROOMS:
        ROOMS[room_code] = []
        
    if request.method == 'GET':
        return jsonify({"messages": ROOMS[room_code]})
        
    elif request.method == 'POST':
        data = request.json or {}
        sender = data.get('sender', 'Anonymous')
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({"error": "Message cannot be empty"}), 400
            
        message = {"sender": sender, "text": text}
        ROOMS[room_code].append(message)
        
        # Keep buffer size manageable
        if len(ROOMS[room_code]) > 50:
            ROOMS[room_code].pop(0)
            
        return jsonify({"success": True, "message": message})

if __name__ == '__main__':
    app.run(debug=True)