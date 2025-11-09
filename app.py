from flask import Flask, render_template,request, jsonify, abort
from database import SessionLocal, SensorReading, User, init_db
from config import API_KEY
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

init_db()

def require_api_key():
    if request.headers.get("X-API-KEY") != API_KEY:
        abort(403, "Forbidden: Invalid API Key")



@app.route('/')
def home():
    return render_template('layout.html')


if __name__ == '__main__':
    app.run(debug=True)
