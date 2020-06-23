# ============== INIT ==============
from flask import Flask, send_from_directory, request, redirect, url_for, render_template, g
from flask_minify import minify
from user_agents import parse as ua_parse
from github.MainClass import Github
import os, json, random, requests, mimetypes
from urllib.parse import quote
from time import time
app = Flask(__name__, template_folder="game")
minify(app=app, html=True, js=True, cssless=True, static=True, caching_limit=0)
if os.getenv("GITHUB_VERSION_PAT") != None:
    gg = Github(os.getenv("GITHUB_VERSION_PAT"))
else:
    gg = Github()
def make_sender(pathy, directy):
    pathy = pathy
    directy = directy
    def f():
        dpathy = os.path.join(app.root_path, "game/"+directy+pathy)
        mimetype = mimetypes.guess_type(pathy)[0]
        return send_from_directory(os.path.join(app.root_path, "game/"+directy),
                                   pathy.replace("/", ""), mimetype=mimetype)
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
        "dp": quote(page),
        "npa": "1",
        "ds": "server%20web",
        "z": str(int(random.random() * pow(10, 25)))
    }
    if ip is not None:
        data['uip'] = ip
    if agent is not None:
        data['ua'] = quote(agent)
    response = requests.post(
        'https://www.google-analytics.com/collect', data=data)
@app.before_request
def before_req():
    g.before_before_request_time = time()
    g.middle_before_request_time = time()
    g.after_before_request_time = time()
    g.after_after_request_time = time()
    if request.headers["X-Forwarded-Proto"] == "http":
        return redirect(request.url.replace("http", "https"), code=301)
    ua = None
    ua_add = ""
    if "User-Agent" in request.headers:
        ua = request.headers["User-Agent"]
        ua_add = ", "+str(ua_parse(ua))
    ip = request.headers["X-Forwarded-For"]
    print("Hit from " + ip + ua_add)
    chunks = request.url.split("/")
    g.middle_before_request_time = time()
    track_view("/".join(chunks[3:len(chunks)]), ip, ua)
    g.after_before_request_time = time()
@app.after_request
def after_req(response):
    response.headers["Content-Security-Policy"] = "default-src https: 'unsafe-eval' 'unsafe-inline'; object-src 'none'"
    response.headers["Content-Security-Policy-Report-Only"] = "default-src https:"
    if response.status_code != 301:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    g.after_after_request_time = time()
    response.headers["Server-Timing"] = "beforereq;desc='Process redirect and log';dur="
    response.headers["Server-Timing"] += str(round(g.middle_before_request_time - g.before_before_request_time, 2))
    response.headers["Server-Timing"] += ", track;desc='Track pageview with Google Analytics';dur="
    response.headers["Server-Timing"] += str(round(g.after_before_request_time - g.middle_before_request_time, 2))
    response.headers["Server-Timing"] += ", process;desc='Render stuff';dur="
    response.headers["Server-Timing"] += str(round(g.after_after_request_time - g.after_before_request_time, 2))
    return response
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
    return render_template("play.html")
#    return "Your ID and PIN are "+theid+", "+thepin
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
    repname = "KTibow/scorecard"
    commits = list(gg.get_repo(repname).get_commits())
    cacheid = str(len(commits))
    sw = sw.replace("INSERT VERSION", cacheid)
    respo = app.make_response(sw)
    respo.mimetype = "application/javascript"
    return respo
