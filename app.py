from flask import (
    Flask, flash, redirect, render_template,
    request, jsonify, abort, url_for, session
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to MySQL
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user and check_password_hash(user['password'], password):
                # Store user session
                session['user_id'] = user['id']
                session['user_name'] = user['name']

                flash("Logged in successfully!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password", "danger")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")

    return render_template('login.html')


# -------------------------------------------------------
# API Key Check
# -------------------------------------------------------
def require_api_key():
    if request.headers.get("X-API-KEY") != API_KEY:
        abort(403, "Forbidden: Invalid API Key")


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first", "warning")
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['user_name'])

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))


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


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    db = SessionLocal()
    user = db.query(User).filter(User.id == session['user_id']).first()
    db.close()

    return render_template('profile.html', user=user)


@app.route('/insights')
def insights():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    return render_template('insights.html')

# -------------------------------------------------------
# Run Server
# -------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
