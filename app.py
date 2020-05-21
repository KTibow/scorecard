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
def make_sender(path):
    def f():
        mimetype = magic.from_file(os.path.join(app.root_path, 'game/browserfiles'+path), mime=True)
        print("I got called to do "+os.path.join(app.root_path, 'game/browserfiles'+path)+" with mimetype of "+mimetype)
        return send_from_directory(os.path.join(app.root_path, 'game/browserfiles'),
                                   path.replace("/", ""), mimetype=mimetype)
    return f
for file in ['/robots.txt', '/android-icon-36x36.png',
             '/android-icon-48x48.png', '/android-icon-72x72.png',
             '/android-icon-96x96.png', '/android-icon-144x144.png',
             '/android-icon-192x192.png', '/apple-icon.png',
             '/apple-icon-57x57.png', '/apple-icon-60x60.png',
             '/apple-icon-72x72.png', '/apple-icon-76x76.png',
             '/apple-icon-114x114.png', '/apple-icon-120x120.png',
             '/apple-icon-144x144.png', '/apple-icon-152x152.png',
             '/apple-icon-180x180.png', '/apple-icon-precomposed.png',
             '/browserconfig.xml', '/favicon-16x16.png',
             '/favicon-32x32.png', '/favicon-96x96.png',
             '/favicon.ico', '/manifest.json',
             '/ms-icon-70x70.png', '/ms-icon-144x144.png',
             '/ms-icon-150x150.png', '/ms-icon-310x310.png']:
    app.add_url_rule(file, file, make_sender(file))
