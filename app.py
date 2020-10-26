"""
This is the scorecard Heroku app. Look at the README for more details.
"""

# ============== INIT ==============

# General stuff
import json
import mimetypes
import os
from random import randint
import time

from flask import (
    Flask,
    g as flask_global,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_minify import minify
from github.MainClass import Github

# Tracking
from user_agents import parse as ua_parse
import hashlib
from urllib.parse import quote
import requests

# Service worker
import threading

# Init flask
app = Flask(__name__, template_folder="game")
minify(app=app, html=True, js=True, cssless=True, static=True, caching_limit=0)
# Init github
if os.getenv("GITHUB_VERSION_PAT") is not None:
    gg = Github(os.getenv("GITHUB_VERSION_PAT"))
    rep = gg.get_repo("KTibow/scorecard")
else:
    gg = Github()
    rep = gg.get_repo("KTibow/scorecard")


def sleep(timefor):
    for _i in range(round(timefor * 16.0)):
        time.sleep(1 / 16)


comm_num = 0


def find_commit():
    # Declarations
    print("Starting commit finder")
    global comm_num
    global gg
    prevcomm = -1
    while True:
        # Get rate limiting and log if it's divisible by 10
        rate_limit = gg.rate_limiting[1]
        rate_limit_remaining = gg.rate_limiting[0]
        rate_limit_used = rate_limit - rate_limit_remaining
        if (rate_limit_used % 10) == 0:
            print(
                "We've used up",
                f"{rate_limit_used}/{rate_limit}",
                "interactions so far",
            )
        prevcomm = comm_num
        try:
            if rate_limit_used < rate_limit * 0.8:
                # Try (prevent exceptions) if there are less than 4/5 interactions used
                # Get commit number (DO NOT use len(list(rep.get_commits())) )
                comm_num = rep.get_commits().totalCount
                # Log if updated
                if prevcomm != comm_num:
                    print(
                        "We updated from",
                        prevcomm,
                        "commits to",
                        comm_num,
                        "commits! (So far we've used",
                        rate_limit_used,
                        "interactions out of",
                        str(rate_limit) + ")",
                    )
                if rate_limit_used > rate_limit * 0.4:
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
        mimetype = mimetypes.guess_type(pathy)[0]
        return send_from_directory(
            os.path.join(app.root_path, "game/" + directy),
            pathy.replace("/", ""),
            mimetype=mimetype,
        )

    return f


def walk():
    pys = []
    for root, _dirs, files in os.walk("game"):
        for file in files:
            if "html" not in file:
                pys.append([root.replace("game/", ""), "/" + file])
    return pys


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def track_view(page, ip, agent):
    data = {
        "v": "1",
        "tid": "UA-165004437-2",
        "cid": hashlib.sha512((str(ip) + str(agent)).encode()).hexdigest(),
        "t": "pageview",
        "dh": "tank-scorecard.herokuapp.com",
        "dp": quote(page),
        "npa": "1",
        "ds": "server",
        "z": str(randint(0, pow(10, 10))),
    }
    if ip is not None:
        data["uip"] = ip
    if agent is not None:
        data["ua"] = quote(agent)
    requests.post("https://www.google-analytics.com/collect", data=data)


@app.before_request
def before_req():
    if "debuggy" not in globals():
        flask_global.before_before_request_time = time.time() * 1000
        flask_global.middle_before_request_time = time.time() * 1000
        flask_global.after_before_request_time = time.time() * 1000
        flask_global.after_after_request_time = time.time() * 1000
        if request.headers["X-Forwarded-Proto"] == "http":
            return redirect(request.url.replace("http", "https"), code=301)
        ua = None
        ua_add = ""
        if "User-Agent" in request.headers:
            ua = request.headers["User-Agent"]
            ua_add = ", " + str(ua_parse(ua))
        ip = request.headers["X-Forwarded-For"]
        print("Hit from " + ip + ua_add)
        chunks = request.url.split("/")
        flask_global.middle_before_request_time = time.time() * 1000
        track_view("/".join(chunks[2 : len(chunks)]), ip, ua)
        flask_global.after_before_request_time = time.time() * 1000


@app.after_request
def after_req(response):
    response.headers[
        "Content-Security-Policy"
    ] = "default-src https: 'unsafe-eval' 'unsafe-inline'; object-src 'none'"
    if response.status_code != 301:
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if "debuggy" not in globals():
        flask_global.after_after_request_time = time.time() * 1000
        server_timing = 'beforereq;desc="Process redirect and log";dur='
        server_timing += str(
            round(
                flask_global.middle_before_request_time
                - flask_global.before_before_request_time,
                1,
            )
        )
        server_timing += ', track;desc="Track pageview";dur='
        server_timing += str(
            round(
                flask_global.after_before_request_time
                - flask_global.middle_before_request_time,
                1,
            )
        )
        server_timing += ', process;desc="Render stuff";dur='
        server_timing += str(
            round(
                flask_global.after_after_request_time
                - flask_global.after_before_request_time,
                1,
            )
        )
        response.headers["Server-Timing"] = server_timing
    return response


# ========== WEB INTERFACE ==========
# home
@app.route("/")
def hello():
    return render_template("welcome.html")


# card
@app.route("/cluecard/<theid>")
def card(theid):
    return render_template("play.html", uid=theid)


# 404
@app.errorhandler(404)
def err404(e):
    if request.url[len(request.url) - 1] == "/":
        return redirect(request.url[0 : len(request.url) - 1], code=301)
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
        id_database = json.load(open("ids.db", "r"))
    except FileNotFoundError:
        id_database = {}
    nid = str(randint(0, 99999)).zfill(5)
    if username in id_database:
        oid = id_database[username]
        try:
            group_database = json.load(open("groups.db", "r"))
        except FileNotFoundError:
            group_database = []
        for gy in group_database:
            group_database[group_database.index(gy)] = [
                x if x != oid else nid for x in gy
            ]
        print(group_database)
        json.dump(group_database, open("groups.db", "w"))
    # First ID
    id_database[username] = nid
    print(id_database)
    json.dump(id_database, open("ids.db", "w"))
    return "/cluecard/" + id_database[username]


@app.route("/addid/<exist>/<new>")
def addid(exist, new):
    exist = exist.zfill(5)
    new = new.zfill(5)
    try:
        aids = list(json.load(open("ids.db", "r")).values())
    except Exception as e:
        print(e)
        aids = []
    if exist not in aids or new not in aids:
        try:
            json.load(open("ids.db", "r"))
        except Exception:
            json.dump({}, open("ids.db", "w"))
        print(
            "These people:",
            exist,
            new,
            "Are not in:",
            aids,
            json.load(open("ids.db", "r")),
            "Exist in:",
            exist in aids,
            "New in:",
            new in aids,
        )
        return "notreal"
    try:
        group_database = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        group_database = []
    for gy in group_database:
        if exist in gy and new in gy:
            return "already"
    comp = [i for x in group_database for i in x]
    if exist in comp and new in comp:
        newgp = []
        for gy in group_database:
            if new in gy:
                newgp = gy
        for gy in group_database:
            if exist in gy:
                group_database[group_database.index(gy)] = (
                    gy + newgp[1 : len(newgp)]
                )
                group_database.remove(newgp)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "merge"
    elif exist in comp and new not in comp:
        for gy in group_database:
            if exist in gy:
                group_database[group_database.index(gy)].append(new)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "addnew"
    elif exist not in comp and new in comp:
        for gy in group_database:
            if new in gy:
                group_database[group_database.index(gy)].append(exist)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "addexist"
    else:
        # Best: Give you answer, finish game
        # Most: Give you what number isn't
        # Couple: Nothing
        infodict = {"rightnum": str(randint(1, 1000))}
        fyet = False
        for tletter in "ABCD":
            for tnumber in range(1, 5):
                myoption = randint(0, 15)
                if myoption == 0:
                    myoption = "0"
                    fyet = True
                elif myoption < 12:
                    myoption = "1"
                else:
                    myoption = "2"
                if tletter + str(tnumber) == "D4" and not fyet:
                    myoption = "0"
                infodict[tletter + str(tnumber)] = myoption
        group_database.append([infodict, exist, new])
        print(group_database)
        json.dump(group_database, open("groups.db", "w"))
        return "makenew"


@app.route("/gids/<uid>")
def fids(uid):
    try:
        group_database = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        group_database = []
    comp = [i for x in group_database for i in x]
    if uid not in comp:
        return "You currently don't have anyone in your group."
    for gy in group_database:
        if uid in gy:
            try:
                id_database = json.load(open("ids.db", "r"))
            except FileNotFoundError:
                id_database = {}
            gy = gy[1 : len(gy)]
            inv_map = {value: key for key, value in id_database.items()}
            mgy = [inv_map[g] for g in gy.copy()]
            return (
                "In your group, there's these people:"
                + f'<span style="color: deepskyblue;">{", ".join(mgy)}</span>'
            )


@app.route("/cardstatus/<uid>/<cardnum>")
def checkcard(uid, cardnum):
    try:
        group_database = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        group_database = []
    comp = [user_id for group in group_database for user_id in group]
    if uid not in comp:
        return "2"
    for group in group_database:
        if uid in group:
            return group[0][cardnum]


@app.route("/rightnum/<uid>")
def rightnum(uid):
    try:
        group_database = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        group_database = []
    comp = [user_id for group in group_database for user_id in group]
    if uid not in comp:
        return "-1"
    for gy in group_database:
        if uid in gy:
            return gy[0]["rightnum"]


# ========== BROWSER FILES ==========
for browser_file in walk():
    print(browser_file)
    if browser_file[1] != "/sw.js":
        app.add_url_rule(
            browser_file[1],
            browser_file[1],
            make_sender(browser_file[1], browser_file[0]),
        )


# ========= SERVICE WORKER =========


@app.route("/sw.js")
def make_service_worker():
    """
    Generate a JS service worker dynamically.

    Returns:
        The errors to ignore, including the default errors.
    """
    links = []
    for rule in app.url_map.iter_rules():
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(f"'{url}'")
    swlist = ""
    for index, link in enumerate(links):
        if len(links) - 1 != index:
            link = f"{link}, "
        swlist += link
    global comm_num
    sw = render_template(
        "browserfiles/sw.js", urls=swlist, version=str(comm_num)
    )
    respo = app.make_response(sw)
    respo.mimetype = "application/javascript"
    return respo
