from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello():
    return open("game/welcome.html", "r").read()
