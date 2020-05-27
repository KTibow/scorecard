# ============== INIT ==============
from flask import Flask, send_from_directory, request, redirect
import os, magic, json
app = Flask(__name__)
def make_sender(path, dir):
    def f():
        mimetype = magic.from_file(os.path.join(app.root_path, 'game/'+dir+path), mime=True)
        if "js" in path:
            mimetype = "application/javascript"
        if "css" in path:
            mimetype = "text/css"
        return send_from_directory(os.path.join(app.root_path, 'game/'+dir),
                                   path.replace("/", ""), mimetype=mimetype)
    return f
def walk():
    pys = []
    for p, d, f in os.walk('game'):
        for file in f:
            if 'html' not in file:
                pys.append([p.replace("game/", ""), "/"+file])
    return pys
@app.before_request
def http_redir():
    if request.headers["X-Forwarded-Proto"] == "http":
        return redirect(request.url.replace("http", "https"), code=301)
# ========== WEB INTERFACE ==========
# home
@app.route('/')
def hello():
    return open("game/welcome.html", "r").read()
# ============== API ================
@app.route('/makeid/<username>')
def genid(username):
    try:
        idDB = json.load(open("ids.db", "r"))
    except FileNotFoundError:
        open("ids.db", "w").close()
        idDB = json.load(open("ids.db", "r"))
    # First ID, then PIN
    idDB[username] = [random.randint(0, 9999), random.randint(0, 9999)]
    print(idDB)
    json.dump(idDB, open("ids.db", "w"))
    return idDB[username]
# ========== BROWSER FILES ==========
for file in walk():
    app.add_url_rule(file[1], file[1], make_sender(file[1], file[0]))
