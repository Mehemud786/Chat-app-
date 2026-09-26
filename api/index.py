from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/status")
def status():
    return jsonify({"status": "online", "service": "Nirnoy Diagnostics P2P Bridge"})

if __name__ == "__main__":
    app.run(debug=True)