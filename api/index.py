from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

# In-memory dictionary to hold room messages 
# Structure: { "1234": [{"sender": "Alice", "text": "Hi everyone!"}] }
ROOMS = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rooms/join', methods=['POST'])
def join_room():
    data = request.json
    room_code = data.get('room_code')
    
    if not room_code or len(str(room_code)) != 4 or not str(room_code).isdigit():
        return jsonify({"error": "Invalid 4-digit room code"}), 400
    
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
        data = request.json
        sender = data.get('sender', 'Anonymous')
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({"error": "Message cannot be empty"}), 400
            
        message = {"sender": sender, "text": text}
        ROOMS[room_code].append(message)
        
        # Keep only the last 50 messages per room to limit memory usage
        if len(ROOMS[room_code]) > 50:
            ROOMS[room_code].pop(0)
            
        return jsonify({"success": True, "message": message})

if __name__ == '__main__':
    app.run(debug=True)