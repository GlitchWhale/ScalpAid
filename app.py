from flask import (
    Flask, flash, redirect, render_template,
    request, jsonify, abort, url_for, session
)
from database import SessionLocal, User
from config import API_KEY, DB_CONFIG, SECRET_KEY
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from pubnub_client import publish_sensor_data

import threading
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback

from datetime import datetime, timedelta

from datetime import datetime
from sqlalchemy import func
from dotenv import load_dotenv
from config import fernet


load_dotenv()



pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-965e4329-6565-4fba-bb02-05774be3a3c3"
pnconfig.publish_key = "pub-c-72867b34-4207-47de-a982-c35d4dbf14a8"
pnconfig.uuid = "flask-server"

pubnub = PubNub(pnconfig)
TEMP_HIGH_THRESHOLD = 40      # TEST MODE
MOISTURE_LOW_THRESHOLD = 20


class ScalpListener(SubscribeCallback):
    def message(self, pubnub, event):
        data = event.message
        print("Received:", data)

        device = data.get("device")
        temperature = data.get("temperature")
        state = data.get("state")
        moisture_raw = data.get("moisture_raw")
        moisture_voltage = data.get("moisture_voltage")
        moisture_percent = data.get("moisture_percent")
        timestamp = data.get("timestamp")

        user_id = data.get("user_id", 1)

        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                port=DB_CONFIG["port"]
            )
            print
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO sensor_readings (
                    device_id,
                    temperature_cipher,
                    moisture_cipher,
                    timestamp,
                    user_id
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                device,
                fernet.encrypt(str(temperature).encode()).decode(),
                fernet.encrypt(str(moisture_percent).encode()).decode(),
                timestamp,
                user_id
            ))

            conn.commit()
            print("Saved to AWS DB.")

        except Exception as e:
            print("DB ERROR:", e)

        finally:
            try:
                cursor.close()
                conn.close()
            except Exception:
                pass


def start_pubnub_listener():
    pubnub.add_listener(ScalpListener())
    pubnub.subscribe().channels("scalp_data").execute()

threading.Thread(target=start_pubnub_listener, daemon=True).start()



app = Flask(__name__)
app.secret_key = SECRET_KEY


# init_db()



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

     
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user and check_password_hash(user['password'], password):
              
                session['user_id'] = user['id']
                session['user_name'] = user['name']

                flash("Logged in successfully!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password", "danger")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")

    return render_template('login.html')



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



@app.route('/sensor-data')
def sensor_data():
    """Frontend page for viewing live sensor data."""
    return render_template('sensor_data.html')


@app.route("/api/sensors/data", methods=["POST"])
def receive_sensor_data():
    """
    Receive temperature and moisture readings from Raspberry Pi,
    store them, and publish via PubNub.
    """

    
    token = request.headers.get("X-API-KEY")
    if token != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    # Validate JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    device_id = data.get("device_id", "unknown")
    temperature = data.get("temperature")
    moisture = data.get("moisture")          # this will also be used as moisture_percent
    user_id = data.get("user_id")

    if temperature is None or moisture is None:
        return jsonify({"error": "temperature and moisture required"}), 400

    

    # --- ALERT LOGIC (backend side) ---
    alert = None

    # Use your thresholds (you can tweak these)
    if temperature is not None and temperature > TEMP_HIGH_THRESHOLD:
        alert = {
            "type": "HIGH_TEMP",
            "message": f"Warning: High temperature detected ({temperature:.1f}°C)",
            "value": float(temperature)
        }
    elif moisture is not None and moisture < MOISTURE_LOW_THRESHOLD:
        alert = {
            "type": "LOW_MOISTURE",
            "message": f"Scalp moisture is low ({moisture:.1f}%)",
            "value": float(moisture)
        }

   
    publish_payload = {
        "device_id": device_id,
        "temperature": temperature,
      
        "moisture_percent": moisture,
        "timestamp": data.get("timestamp"),
        "alert": alert
    }

    publish_sensor_data(publish_payload)

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


from ai_utils import get_insights_page_ai
# ... already imported datetime, timezone ...


@app.route('/insights')
def insights():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    # Get last 7 days of readings from sensor_readings table
    readings_last_7_days = []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        seven_days_ago_ts = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())

        cursor.execute("""
            SELECT temperature_cipher, moisture_cipher, timestamp
            FROM sensor_readings
            WHERE timestamp >= %s
            ORDER BY timestamp DESC
        """, (seven_days_ago_ts,))


        rows = cursor.fetchall()
        for r in rows:
            try:
                temperature = fernet.decrypt(
                    r["temperature_cipher"].encode()
                ).decode()
            except Exception:
                temperature = None

            try:
                moisture = fernet.decrypt(
                    r["moisture_cipher"].encode()
                ).decode()
            except Exception:
                moisture = None

            readings_last_7_days.append({
                "temperature": temperature,
                "moisture_percent": moisture,
                "timestamp": datetime.fromtimestamp(
                    int(r["timestamp"]), tz=timezone.utc
                ),
            })

    except Exception as e:
        print("DB ERROR insights:", e)
        flash("Error fetching insights data.", "danger")

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

    # Get user for context
    db = SessionLocal()
    user = db.query(User).filter(User.id == session['user_id']).first()
    db.close()

    ai_insights_text = None
    try:
        ai_insights_text = get_insights_page_ai(readings_last_7_days, user=user)
    except Exception as e:
        print("[AI ERROR insights]", e)

    return render_template(
        "insights.html",
        ai_insights=ai_insights_text,
    )



from datetime import datetime, timedelta

from datetime import datetime, timedelta
import pytz

from datetime import datetime, timezone

from ai_utils import get_history_ai_insights
# ... existing imports above ...


@app.route('/history', methods=['GET'])
def history():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    selected_date = request.args.get('date')
    history_entries = []

    LOCAL_TZ = pytz.timezone("Europe/Dublin")

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        if selected_date:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

            # Define start/end of that day in LOCAL time
            start_local = LOCAL_TZ.localize(datetime.combine(date_obj, datetime.min.time()))
            end_local = LOCAL_TZ.localize(datetime.combine(date_obj, datetime.max.time()))

            start_ts = int(start_local.astimezone(timezone.utc).timestamp())
            end_ts = int(end_local.astimezone(timezone.utc).timestamp())

            cursor.execute("""
                SELECT * FROM sensor_readings
                WHERE timestamp BETWEEN %s AND %s
                ORDER BY timestamp DESC
            """, (start_ts, end_ts))

        else:
            cursor.execute("""
                SELECT * FROM sensor_readings
                ORDER BY timestamp DESC
                LIMIT 100
            """)

        rows = cursor.fetchall()

        for r in rows:
            ts_utc = datetime.fromtimestamp(int(r["timestamp"]), tz=timezone.utc)
            ts_local = ts_utc.astimezone(LOCAL_TZ)

            # Decrypt values
            try:
                temperature = fernet.decrypt(r['temperature_cipher'].encode()).decode()
            except:
                temperature = "N/A"

                # decrypt moisture
                try:
                    moisture = fernet.decrypt(r['moisture_cipher'].encode()).decode()
                except:
                    moisture = "N/A"

            history_entries.append({
                "type": "sensor",
                "title": "Sensor Log Recorded",
                "details": f"Temperature: {temperature}°C • Moisture: {moisture}%",
                "timestamp": ts_local
            })

        if not rows:
            history_entries.append({
                "type": "sensor",
                "title": "No activity",
                "details": f"No sensor data recorded.",
                "timestamp": datetime.now(LOCAL_TZ),
            })

    except Exception as e:
        print("DB ERROR:", e)
        flash("Error fetching sensor history.", "danger")

    finally:
        try: cursor.close()
        except: pass
        try: conn.close()
        except: pass

    # User context for AI
    db = SessionLocal()
    user = db.query(User).filter(User.id == session['user_id']).first()
    db.close()

    # 🔥 Restore AI insight generation
    ai_history_insights = None
    try:
        ai_history_insights = get_history_ai_insights(history_entries, user=user)
    except Exception as e:
        print("[AI ERROR history]", e)

    return render_template(
        "history.html",
        history=history_entries,
        selected_date=selected_date,
        ai_history_insights=ai_history_insights,
    )





@app.route("/pi")
def pi_page():
    return render_template("pi.html")

@app.route("/start_pi")
def start_pi():
    pubnub.publish().channel("scalp_commands").message({"command": "start"}).sync()
    return redirect(url_for("pi_page"))

@app.route("/stop_pi")
def stop_pi():
    pubnub.publish().channel("scalp_commands").message({"command": "stop"}).sync()
    return redirect(url_for("pi_page"))


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    if count > 0:
        return redirect(url_for('login'))

    return render_template('home.html')

@app.context_processor
def inject_user_state():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return {"users_exist": count > 0}



if __name__ == '__main__':
    app.run(debug=True)
