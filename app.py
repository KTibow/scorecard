# ============== INIT ==============
from flask import Flask, send_from_directory, request, redirect
from flask_minify import minify
import os, magic
app = Flask(__name__)
minify(app=app, html=True, js=True, cssless=True, caching_limit=0)
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
@app.before_request
def http_redir():
    if request.headers["X-Forwarded-Proto"] == "http":
        return redirect(request.url.replace("http", "https"), code=301)
# ========== WEB INTERFACE ==========
# home
@app.route('/')
def hello():
    return open("game/welcome.html", "r").read()
# ===== RELATED TO WEB INTERFACE ====
for file in ['/welcome.css', '/install.js']:
    app.add_url_rule(file, file, make_sender(file, "related"))
# ============== API ================

# ========== BROWSER FILES ==========
for file in ['/robots.txt', '/android-icon-36x36.png',
             '/android-icon-48x48.png', '/android-icon-72x72.png',
             '/android-icon-96x96.png', '/android-icon-144x144.png',
             '/android-icon-192x192.png', '/apple-icon.png',
             '/apple-icon-57x57.png', '/apple-icon-60x60.png',
             '/apple-icon-72x72.png', '/apple-icon-76x76.png',
             '/apple-icon-114x114.png', '/apple-icon-120x120.png',
             '/apple-icon-144x144.png', '/apple-icon-152x152.png',
             '/apple-icon-180x180.png', '/apple-icon-precomposed.png',
             '/browserconfig.xml', '/favicon-16x16.png', '/sw.js',
             '/favicon-32x32.png', '/favicon-96x96.png',
             '/favicon.ico', '/manifest.json', '/maskable_icon.png',
             '/ms-icon-70x70.png', '/ms-icon-144x144.png',
             '/ms-icon-150x150.png', '/ms-icon-310x310.png']:
    app.add_url_rule(file, file, make_sender(file, "browserfiles"))
for file in ['/open-sans.eot', '/open-sans.svg', '/open-sans.ttf',
             '/open-sans.woff', '/open-sans.woff2']:
    app.add_url_rule(file, file, make_sender(file, "fonts"))
