# ============== INIT ==============
# Flask
from flask import Flask, send_from_directory, request, redirect, url_for, render_template, g
from flask_minify import minify
# Various
import os
from random import randint
# sw.js
from github.MainClass import Github
from time import sleep as tm_sleep
from threading import Thread
# Database
import json
# Static files
import mimetypes
# Tracking
from urllib.parse import quote
import requests
from user_agents import parse as ua_parse
# Server-side timing
from time import time
# Init flask
app = Flask(__name__, template_folder="game")
minify(app=app, html=True, js=True, cssless=True, static=True, caching_limit=0)
# Init github
if os.getenv("GITHUB_VERSION_PAT") != None:
    gg = Github(os.getenv("GITHUB_VERSION_PAT"))
    rep = gg.get_repo("KTibow/scorecard")
else:
    gg = Github()
    rep = gg.get_repo("KTibow/scorecard")
def sleep(timefor):
    for i in range(round(timefor * 2)):
        tm_sleep(0.5)
comm_num = 0
def find_commit(id):
    print("Starting commit finder")
    global comm_num
    global gg
    prevcomm = -1
    while True:
        ratey = gg.rate_limiting
        print("We've used up", ratey[1] - ratey[0], "interactions so far")
        print("In an hour, we'll be back to", ratey[1], "remaining")
        prevcomm = comm_num
        try:
            if ratey[1] - ratey[0] < 4000:
                stint = ratey[1] - ratey[0]
                comm_num = rep.get_commits().totalCount
                ratey = gg.rate_limiting
                endint = ratey[1] - ratey[0]
                if endint <= 2000:
                    print("Getting commits went from", stint, "interactions to", endint, "interactions")
                else:
                    print("Getting commits went from", stint, "interactions to", endint, "interactions (sleeping extra 30 seconds)")
                if prevcomm != comm_num:
                    print("We updated from", prevcomm, "commits to", comm_num, "commits!")
                if endint > 2000:
                    sleep(30)
            else:
                print("Pausing fetch commits")
                sleep(120)
        except Exception as e:
            print(e)
            sleep(240)
        sleep(60)
fc = Thread(target=find_commit, daemon=True)
fc.start()
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
        "z": str(randint(0, 999999999999999))
    }
    if ip is not None:
        data["uip"] = ip
    if agent is not None:
        data["ua"] = quote(agent)
    response = requests.post(
        "https://www.google-analytics.com/collect", data=data)
@app.before_request
def before_req():
    g.before_before_request_time = time() * 1000
    g.middle_before_request_time = time() * 1000
    g.after_before_request_time = time() * 1000
    g.after_after_request_time = time() * 1000
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
    g.middle_before_request_time = time() * 1000
    track_view("/".join(chunks[3:len(chunks)]), ip, ua)
    g.after_before_request_time = time() * 1000
@app.after_request
def after_req(response):
    response.headers["Content-Security-Policy"] = "default-src https: 'unsafe-eval' 'unsafe-inline'; object-src 'none'"
    response.headers["Content-Security-Policy-Report-Only"] = "default-src https:"
    if response.status_code != 301:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    g.after_after_request_time = time() * 1000
    response.headers["Server-Timing"] = "beforereq;desc=\"Process redirect and log\";dur="
    response.headers["Server-Timing"] += str(round(g.middle_before_request_time - g.before_before_request_time, 1))
    response.headers["Server-Timing"] += ", track;desc=\"Track pageview\";dur="
    response.headers["Server-Timing"] += str(round(g.after_before_request_time - g.middle_before_request_time, 1))
    response.headers["Server-Timing"] += ", process;desc=\"Render stuff\";dur="
    response.headers["Server-Timing"] += str(round(g.after_after_request_time - g.after_before_request_time, 1))
    return response
# ========== WEB INTERFACE ==========
# home
@app.route("/")
def hello():
    return open("game/welcome.html", "r").read()
# join
@app.route("/join")
def join():
    return open("game/join.html", "r").read()
# card
@app.route("/cluecard/<theid>/<thepin>")
def card(theid, thepin):
    return render_template("play.html")
#    return "Your ID and PIN are "+theid+", "+thepin
# ============== API ================
@app.route("/makeid/<username>")
def genid(username):
    username = username.lower()
    try:
        idDB = json.load(open("ids.db", "r"))
    except FileNotFoundError:
        idDB = {}
    # First ID, then PIN
    idDB[username] = [randint(0, 9999), randint(0, 9999)]
    print(idDB)
    json.dump(idDB, open("ids.db", "w"))
    return "/cluecard/" + str(idDB[username][0]) + "/" + str(idDB[username][1])
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
    global comm_num
    cacheid = str(comm_num)
    sw = sw.replace("INSERT VERSION", cacheid)
    respo = app.make_response(sw)
    respo.mimetype = "application/javascript"
    return respo
