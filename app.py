# ============== INIT ==============
from flask import Flask, send_from_directory, request, redirect, url_for
from flask_minify import minify
from user_agents import parse as ua_parse
from github.MainClass import Github
import os, magic, json, random, requests
app = Flask(__name__)
minify(app=app, html=True, js=True, cssless=True, static=True, caching_limit=0)
gg = Github(os.getenv("GITHUB_VERSION_PAT"))
def make_sender(path, dir):
    def f():
        mimetype = magic.from_file(os.path.join(app.root_path, "game/"+dir+path), mime=True)
        if "js" in path:
            mimetype = "application/javascript"
        if "css" in path:
            mimetype = "text/css"
        return send_from_directory(os.path.join(app.root_path, "game/"+dir),
                                   path.replace("/", ""), mimetype=mimetype)
    return f
def walk():
    pys = []
    for p, d, f in os.walk("game"):
        for file in f:
            if "html" not in file:
                pys.append([p.replace("game/", ""), "/"+file])
    return pys
def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)
def track_view(page, ip, agent):
    data = {
        "v": "1",
        "tid": "UA-165004437-2",
        "cid": "555",
        "t": "pageview",
        "dh": "tank-scorecard.herokuapp.com",
        "dp": page
    }
    if ip is not None:
        data['uip'] = ip
    if ua is not None:
        data['ua'] = agent
    response = requests.post(
        'https://www.google-analytics.com/collect', data=data)
    response.raise_for_status()
@app.before_request
def before_req():
    if request.headers["X-Forwarded-Proto"] == "http":
        return redirect(request.url.replace("http", "https"), code=301)
    ua = None
    ua_add = ""
    if "User-Agent" in request.headers:
        ua = request.headers["User-Agent"]
        ua_add = ", "+str(ua_parse(ua))
    ip = request.remote_addr
    print("Hit from "+ip+ua_add)
    chunks = request.url.split("/")
    track_view("/".join(chunks[3:len(chunks)]), ip, ua)
    
# ========== WEB INTERFACE ==========
# home
@app.route('/')
def hello():
    return open("game/welcome.html", "r").read()
# join
@app.route('/join')
def join():
    return open("game/join.html", "r").read()
# card
@app.route('/cluecard/<theid>/<thepin>')
def card(theid, thepin):
    return "Your ID and PIN are "+theid+", "+thepin
# ============== API ================
@app.route('/makeid/<username>')
def genid(username):
    username = username.lower()
    try:
        idDB = json.load(open("ids.db", "r"))
    except FileNotFoundError:
        idDB = {}
    # First ID, then PIN
    idDB[username] = [random.randint(0, 9999), random.randint(0, 9999)]
    print(idDB)
    json.dump(idDB, open("ids.db", "w"))
    return "/cluecard/"+str(idDB[username][0])+"/"+str(idDB[username][1])
# ========== BROWSER FILES ==========
for file in walk():
    if file[1] != "/sw.js":
        app.add_url_rule(file[1], file[1], make_sender(file[1], file[0]))
# ========= SERVICE WORKER =========
@app.route("/sw.js")
def makeserviceworker():
    links = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append("'"+url+"'")
    swlist = ""
    for i, link in enumerate(links):
        swlist += link
        if len(links) - 1 != i:
            swlist += ", "
    sw = open("game/browserfiles/sw.js", "r").read()
    sw = sw.replace("INSERT URLS", swlist)
    commits = list(gg.get_repo("KTibow/scorecard").get_commits())
    cacheid = str(len(commits))
    sw = sw.replace("INSERT VERSION", cacheid)
    return sw
