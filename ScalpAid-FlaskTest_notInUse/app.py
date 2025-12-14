from flask import Flask, jsonify
import mysql.connector
import threading
from flask import redirect, url_for

from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "scalpaid_test"
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# PubNub setup
pnconfig = PNConfiguration()
pnconfig.publish_key = "pub-c-72867b34-4207-47de-a982-c35d4dbf14a8"
pnconfig.subscribe_key = "sub-c-965e4329-6565-4fba-bb02-05774be3a3c3"
pnconfig.uuid = "flask-server"
pubnub = PubNub(pnconfig)

# Listener for sensor messages
class ScalpListener(SubscribeCallback):
    def message(self, pubnub, event):
        data = event.message
        print("Received:", data)

        device = data.get("device")
        temperature = data.get("temperature")
        state = data.get("state")
        moisture_raw = data.get("moisture_raw")
        moisture_voltage = data.get("moisture_voltage")
        timestamp = data.get("timestamp")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO readings (device, temperature, state, moisture_raw, moisture_voltage, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (device, temperature, state, moisture_raw, moisture_voltage, timestamp)
        )

        conn.commit()
        cursor.close()
        conn.close()

def start_pubnub():
    pubnub.add_listener(ScalpListener())
    pubnub.subscribe().channels("scalp_data").execute()

threading.Thread(target=start_pubnub, daemon=True).start()

@app.route("/")
def index():
    return """
        <h1>ScalpAid API</h1>
        <p>System running.</p>

        <a href='/start_pi'>
            <button style="padding:10px;font-size:18px;">Start Sensor Readings</button>
        </a>

        <br><br>

        <a href='/stop_pi'>
            <button style="padding:10px;font-size:18px;">Stop Sensor Readings</button>
        </a>

        <br><br>

        <a href='/readings'>View Readings</a>
    """

@app.route("/start_pi")
def start_pi():
    pubnub.publish().channel("scalp_commands").message({"command": "start"}).sync()
    return redirect(url_for('index'))

@app.route("/stop_pi")
def stop_pi():
    pubnub.publish().channel("scalp_commands").message({"command": "stop"}).sync()
    return redirect(url_for('index'))


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
