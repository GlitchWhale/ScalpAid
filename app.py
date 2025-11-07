from flask import Flask
app = Flask(__name__)


@app.route('/')
def Home():
    return "Welcome to Scalp Aid "


if __name__ == '__main__':
    app.run(debug=True)
