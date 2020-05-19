from flask import Flask
app = Flask(__name__)

# home
@app.route('/')
def hello():
    return open("game/welcome.html", "r").read()
# robots.txt
@app.route('/robots.txt')
def robo():
    return open("game/robots.txt", "r").read()
