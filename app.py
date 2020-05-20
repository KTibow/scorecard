from flask import Flask, send_from_directory
import os
app = Flask(__name__)
# ========== WEB INTERFACE ==========
# home
@app.route('/')
def hello():
    return open("game/welcome.html", "r").read()
# ============== API ================

# ========== BROWSER FILES ==========
# robots.txt
@app.route('/robots.txt')
def robo():
    return open("game/robots.txt", "r").read()
# favicon.ico
@app.route('/favicon.ico')
def ico():
    return send_from_directory(os.path.join(app.root_path, 'game'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
