from flask import Flask, jsonify
import mysql.connector
import time
import threading

#pubnub imports
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback

app = Flask(__name__)

# ---- DATABASE CONFIG ----
DB_CONFIG = {
    "host": "localhost",
    "user": "root",         
    "password": "", 
    "database": "scalpaid_test"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

#pubnub config
pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-965e4329-6565-4fba-bb02-05774be3a3c3" 
pnconfig.uuid = "flask-server"
pubnub = PubNub(pnconfig)

class ScalpListener(SubscribeCallback):
    def message(self, pubnub, event):
        data = event.message
        
        # Expected message format:
        # { "device": "pi1", "temperature": 30.0, "state": "warn", "timestamp": 12345678 }

        print("Received from PubNub:", data)

        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO readings (device, temperature, state, timestamp)
            VALUES (%s, %s, %s, %s)
            """,
            (data.get("device"), data.get("temperature"), data.get("state"), data.get("timestamp"))
        )

        conn.commit()
        cursor.close()
        conn.close()
        
        
# Attach listener & subscribe
def start_pubnub():
    pubnub.add_listener(ScalpListener())
    pubnub.subscribe().channels("scalp_data").execute()

# Run PubNub listener in background thread
threading.Thread(target=start_pubnub, daemon=True).start()

@app.route("/")
def index():
    return (
        "<h1>ScalpAid API</h1>"
        "<p>PubNub listener running in background.<br>"
        "Visit <a href='/readings'>/readings</a> to view stored sensor data.</p>"
    )

@app.route("/readings")
def get_readings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)