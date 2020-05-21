from flask import Flask, send_from_directory
import os, magic
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
# ============ FAVICONS ============
def make_sender(path):
    def f():
        return send_from_directory(os.path.join(app.root_path, 'game'),
                                   path, mimetype='image/vnd.microsoft.icon')
    return f
for file in ['/android-icon-36x36.png', '/android-icon-48x48.png', '/android-icon-72x72.png', '/android-icon-96x96.png']:
    app.add_url_rule(file, file, make_sender(file))
