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
    token = request.headers.get("X-API-KEY")
    if token != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON"}), 400

    device = data.get("device_id", "unknown")
    temperature = data.get("temperature")
    moisture = data.get("moisture")
    timestamp = data.get("timestamp", int(time.time()))

    if temperature is None or moisture is None:
        return jsonify({"error": "temperature and moisture required"}), 400

    db = SessionLocal()
    try:
        # temperature row
        temp_row = SensorReading(
            device=device,
            sensor_type="temperature",
            value=float(temperature),
            state=data.get("state", "normal"),
            timestamp=timestamp
        )
        db.add(temp_row)

        # moisture row
        moisture_row = SensorReading(
            device=device,
            sensor_type="moisture",
            value=float(moisture),
            state="normal",
            timestamp=timestamp
        )
        db.add(moisture_row)

        db.commit()

    except Exception as e:
        db.rollback()
        print("DB ERROR:", e)
        return jsonify({"error": "Database failure"}), 500

    finally:
        db.close()

    return jsonify({"status": "ok"}), 200


# -------------------------------------------------------
# Run Server
# -------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
