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
import threading
# Database
import json
# Static files
import mimetypes
# Tracking
from urllib.parse import quote
import requests
import hashlib
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
    for i in range(round(timefor * 16.0)):
        tm_sleep(1 / 16)
comm_num = 0
def find_commit():
    # Declarations
    print("Starting commit finder")
    global comm_num
    global gg
    prevcomm = -1
    while True:
        # Get rate limiting and log if it's divisible by 10
        ratey = gg.rate_limiting
        if (((ratey[1] - ratey[0]) % 10) == 0):
            print("We've used up", str(ratey[1] - ratey[0]) + "/" + str(ratey[1]), "interactions so far")
        prevcomm = comm_num
        try:
            if ratey[1] - ratey[0] < ratey[1] * 0.8:
                # Try (prevent exceptions) if there are less than 4/5 interactions used
                # Get commit number (DO NOT use len(list(rep.get_commits())) )
                comm_num = rep.get_commits().totalCount
                # Get rate limiting and get used interactions
                ratey = gg.rate_limiting
                endint = ratey[1] - ratey[0]
                # Log if updated
                if prevcomm != comm_num:
                    print("We updated from", prevcomm, "commits to", comm_num, "commits! (So far we've used", endint, "interactions out of", str(ratey[1]) + ")")
                if endint > ratey[1] * 0.4:
                    # If more than 2/5 interactions used, log and sleep
                    print("(sleeping extra 30 seconds in commit fetcher)")
                    sleep(30)
            else:
                # Pause until next reset
                print("Pausing fetch commits")
                sleep(120)
        except Exception as e:
            # Log exception and wait (in case of other rate limit)
            print(e)
            sleep(240)
        # Sleep (don't use up rate limit)
        sleep(60)
# Start async commit checker
fc = threading.Thread(target=find_commit, daemon=True)
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
        "cid": hashlib.md5((str(ip) + str(agent)).encode()).hexdigest(),
        "t": "pageview",
        "dh": "tank-scorecard.herokuapp.com",
        "dp": quote(page),
        "npa": "1",
        "ds": "server",
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
    if "debuggy" not in globals():
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
        track_view("/".join(chunks[2:len(chunks)]), ip, ua)
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
    if "debuggy" not in globals():
        g.after_after_request_time = time() * 1000
        response.headers["Server-Timing"] = "beforereq;desc=\"Process redirect and log\";dur="
        response.headers["Server-Timing"] += str(round(g.middle_before_request_time - g.before_before_request_time, 1))
        response.headers["Server-Timing"] += ", track;desc=\"Track pageview\";dur="
        response.headers["Server-Timing"] += str(round(g.after_before_request_time - g.middle_before_request_time, 1))
        response.headers["Server-Timing"] += ", p43240rocess;desc=\"Render stuff\";dur="
        response.headers["Server-Timing"] += str(round(g.after_after_request_time - g.after_before_request_time, 1))
    return response
# ========== WEB INTERFACE ==========
# home
@app.route("/")
def hello():
    return render_template("welcome.html")
# join
@app.route("/join")
def join():
    return render_template("join.html")
# card
@app.route("/cluecard/<theid>/<thepin>")
def card(theid, thepin):
    return render_template("play.html", uid=theid, upin=thepin)
# 404
@app.errorhandler(404)
def err404(e):
    if request.url[len(request.url)-1] == "/":
        return redirect(request.url[0:len(request.url)-1], code=301)
    return render_template("404.html"), 404
@app.route("/404")
def ex404():
    return render_template("404.html")
# 500
@app.errorhandler(500)
def err500(e):
    return render_template("500.html"), 500
# ============== API ================
@app.route("/makeid/<username>")
def genid(username):
    username = username.lower()
    try:
        idDB = json.load(open("ids.db", "r"))
    except FileNotFoundError:
        idDB = {}
    nid = str(randint(0, 99999)).zfill(5)
    if username in idDB:
        oid = idDB[username][0]
        try:
            groupDB = json.load(open("groups.db", "r"))
        except FileNotFoundError:
            groupDB = []
        for gy in groupDB:
            groupDB[groupDB.index(gy)] = [x if x != oid else nid for x in gy]
        print(groupDB)
        json.dump(groupDB, open("groups.db", "w"))
    # First ID, then PIN
    idDB[username] = [nid, str(randint(0, 99999)).zfill(5)]
    print(idDB)
    json.dump(idDB, open("ids.db", "w"))
    return "/cluecard/" + idDB[username][0] + "/" + idDB[username][1]
@app.route("/addid/<exist>/<new>")
def addid(exist, new):
    exist = exist.zfill(5)
    new = new.zfill(5)
    try:
        aids = [a for a, b in json.load(open("ids.db", "r")).values()]
    except Exception as e:
        print(e)
        aids = []
    if exist not in aids or new not in aids:
        print("These people:", exist, new, "Are not in:", aids, json.load(open("ids.db", "r")), "Exist in:", exist in aids, "New in:", new in aids)
        return "notreal"
    try:
        groupDB = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        groupDB = []
    for gy in groupDB:
        if exist in gy and new in gy:
            return "already"
    comp = [i for x in groupDB for i in x]
    if exist in comp and new in comp:
        newgp = []
        for gy in groupDB:
            if new in gy:
                newgp = gy
        for gy in groupDB:
            if exist in gy:
                groupDB[groupDB.index(gy)] = gy + newgp
                groupDB.remove(newgp)
                print(groupDB)
                json.dump(groupDB, open("groups.db", "w"))
                return "merge"
    elif exist in comp and new not in comp:
        for gy in groupDB:
            if exist in gy:
                groupDB[groupDB.index(gy)].append(new)
                print(groupDB)
                json.dump(groupDB, open("groups.db", "w"))
                return "addnew"
    elif exist not in comp and new in comp:
        for gy in groupDB:
            if new in gy:
                groupDB[groupDB.index(gy)].append(exist)
                print(groupDB)
                json.dump(groupDB, open("groups.db", "w"))
                return "addexist"
    else:
        groupDB.append([exist, new])
        print(groupDB)
        json.dump(groupDB, open("groups.db", "w"))
        return "makenew"
@app.route("/gids/<uid>")
def fids(uid):
    try:
        groupDB = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        groupDB = []
    comp = [i for x in groupDB for i in x]
    if uid not in comp:
        return "You currently don't have anyone in your group."
    for gy in groupDB:
        if uid in gy:
            try:
                idDB = json.load(open("ids.db", "r"))
            except FileNotFoundError:
                idDB = {}
            inv_map = {v[0]: k for k, v in idDB.items()}
            mgy = [inv_map[g] for g in gy.copy()]
            return "In your group, there's these people: <span style=\"color: deepskyblue;\">" + ", ".join(mgy) + "</span>"
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
    global comm_num
    sw = render_template("browserfiles/sw.js", urls=swlist, version=str(comm_num))
    respo = app.make_response(sw)
    respo.mimetype = "application/javascript"
    return respo
