from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlite3
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
DB_FILE = "game.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        coins INTEGER DEFAULT 0,
        farm_level INTEGER DEFAULT 1,
        last_harvest REAL DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (username) VALUES (?)", (username,))
        conn.commit()
        return jsonify({"message": "Player registered!", "username": username}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already taken"}), 400

@app.route('/player/<username>', methods=['GET'])
def get_player(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
    player = cursor.fetchone()
    if player:
        return jsonify({"id": player[0], "username": player[1], "coins": player[2], "farm_level": player[3], "last_harvest": player[4]})
    return jsonify({"error": "Player not found"}), 404

@app.route('/click/<username>', methods=['POST'])
def click(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT coins, farm_level FROM players WHERE username = ?", (username,))
    player = cursor.fetchone()
    if player:
        coins = player[0] + 1
        cursor.execute("UPDATE players SET coins = ? WHERE username = ?", (coins, username))
        conn.commit()
        return jsonify({"message": "Click registered!", "coins": coins})
    return jsonify({"error": "Player not found"}), 404

@app.route('/harvest/<username>', methods=['POST'])
def harvest(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT coins, farm_level, last_harvest FROM players WHERE username = ?", (username,))
    player = cursor.fetchone()
    if player:
        now = time.time()
        last_harvest = player[2]
        if now - last_harvest >= 5:  # 5-second interval
            coins = player[0] + player[1] * 10
            cursor.execute("UPDATE players SET coins = ?, last_harvest = ? WHERE username = ?", (coins, now, username))
            conn.commit()
            return jsonify({"message": "Harvest complete!", "coins": coins})
        else:
            return jsonify({"error": "Too soon to harvest!"}), 400
    return jsonify({"error": "Player not found"}), 404

@socketio.on('connect')
def on_connect():
    print("A player connected!")
    emit('message', {'message': 'Welcome to Click & Farm!'})

@socketio.on('update')
def on_update(data):
    emit('update', data, broadcast=True)

if __name__ == "__main__":
    init_db()
    socketio.run(app, host="0.0.0.0", port=5000)