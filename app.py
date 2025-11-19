from flask import (
    Flask, flash, redirect, render_template,
    request, jsonify, abort, url_for
)
from database import SessionLocal, SensorReading, User, init_db
from config import API_KEY, DB_CONFIG, SECRET_KEY
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from pubnub_client import publish_sensor_data

# -------------------------------------------------------
# Flask Setup
# -------------------------------------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Initialize database tables
init_db()


# -------------------------------------------------------
# Registration Page
# -------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_password = generate_password_hash(request.form['password'])

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, hair_type, purpose, password)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                request.form['name'],
                request.form['email'],
                request.form['hair_type'],
                request.form['purpose'],
                hashed_password
            ))
            conn.commit()
            cursor.close()
            conn.close()

            flash("Registration successful!", "success")
            return redirect(url_for('register'))

        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")

    return render_template('register.html')


# -------------------------------------------------------
# API Key Check
# -------------------------------------------------------
def require_api_key():
    if request.headers.get("X-API-KEY") != API_KEY:
        abort(403, "Forbidden: Invalid API Key")


# -------------------------------------------------------
# Home Route
# -------------------------------------------------------
@app.route('/')
def home():
    return render_template('layout.html')


# -------------------------------------------------------
# SENSOR DATA DASHBOARD PAGE (NEW!)
# -------------------------------------------------------
@app.route('/sensor-data')
def sensor_data():
    """Frontend page for viewing live sensor data."""
    return render_template('sensor_data.html')


# -------------------------------------------------------
# API: Receive Sensor Data from Raspberry Pi
# -------------------------------------------------------
@app.route("/api/sensors/data", methods=["POST"])
def receive_sensor_data():
    """
    Receive temperature and moisture readings from Raspberry Pi,
    store them, and publish via PubNub.
    """

    # Check API key
    token = request.headers.get("X-API-KEY")
    if token != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Validate JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    device_id = data.get("device_id", "unknown")
    temperature = data.get("temperature")
    moisture = data.get("moisture")

    if temperature is None or moisture is None:
        return jsonify({"error": "temperature and moisture required"}), 400

    # Save to database
    db = SessionLocal()
    try:
        reading = SensorReading(
            device_id=device_id,
            moisture_cipher="",
            temperature_cipher=""
        )

        reading.set_moisture(str(moisture))
        reading.set_temperature(str(temperature))

        db.add(reading)
        db.commit()
        print(f"[DB] Saved reading from {device_id}")

    except Exception as e:
        db.rollback()
        print("[DB ERROR]", e)
        return jsonify({"error": "Database error"}), 500

    finally:
        db.close()

    # Publish to PubNub (for live dashboard updates)
    publish_sensor_data({
        "device_id": device_id,
        "temperature": temperature,
        "moisture": moisture,
        "timestamp": data.get("timestamp")
    })

    return jsonify({"status": "success"}), 200


# -------------------------------------------------------
# Run Server
# -------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
