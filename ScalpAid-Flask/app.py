from flask import Flask, jsonify
import mysql.connector
import time

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

@app.route("/add_test")
def add_test():
    print("Running /add_test route")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    device = "test_pi"
    temp = 29.75
    state = "warn"
    ts = int(time.time())

    cursor.execute(
        """
        INSERT INTO readings (device, temperature, state, timestamp)
        VALUES (%s, %s, %s, %s)
        """,
        (device, temp, state, ts)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return "Inserted test row into readings table!"

@app.route("/readings")
def get_readings():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM readings ORDER BY id DESC LIMIT 20"
    )
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(rows)

@app.route("/")
def index():
    return (
        "<h1>ScalpAid Test API</h1>"
        "<p>Go to <a href='/add_test'>/add_test</a> to insert a test row.<br>"
        "Then check <a href='/readings'>/readings</a> to see data.</p>"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
