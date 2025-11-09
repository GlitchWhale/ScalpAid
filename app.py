from flask import (
    Flask, flash, redirect, render_template,
    request, jsonify, abort, url_for
)
from database import SessionLocal, SensorReading, User, init_db
from config import API_KEY
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG, SECRET_KEY
import mysql.connector

app = Flask(__name__)
app.secret_key = SECRET_KEY
init_db()


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
            """, (request.form['name'], request.form['email'],
                  request.form['hair_type'], request.form['purpose'],
                  hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Registration successful!", "success")
            return redirect(url_for('register'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")

    return render_template('register.html')


def require_api_key():
    if request.headers.get("X-API-KEY") != API_KEY:
        abort(403, "Forbidden: Invalid API Key")


@app.route('/')
def home():
    return render_template('layout.html')


if __name__ == '__main__':
    app.run(debug=True)
