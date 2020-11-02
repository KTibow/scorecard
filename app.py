"""This is the scorecard Heroku app. Look at the README for more details."""

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
# Init github
if os.getenv("GITHUB_VERSION_PAT") is not None:
    github_instance = Github(os.getenv("GITHUB_VERSION_PAT"))
    rep = github_instance.get_repo("KTibow/scorecard")
else:
    github_instance = Github()
    rep = github_instance.get_repo("KTibow/scorecard")


def sleep(timefor):
    """
    Sleep, but catch interrupts and whatever.

    Args:
        timefor: The amount of time to sleep in seconds.
    """
    for _index in range(round(timefor * 16.0)):
        time.sleep(1 / 16)


comm_num = 0


def find_commit():
    """Continously check for new commits, for the service worker version."""
    # Declarations
    print("Starting commit finder")
    global github_instance
    global comm_num
    prevcomm = -1
    while True:
        # Get rate limiting and log if it's divisible by 10
        rate_limit = github_instance.rate_limiting[1]
        rate_limit_remaining = github_instance.rate_limiting[0]
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
        except Exception as github_error:
            # Log exception and wait (in case of other rate limit)
            print(github_error)
            sleep(240)
        # Sleep (don't use up rate limit)
        sleep(60)


# Start async commit checker
find_commit_thread = threading.Thread(target=find_commit, daemon=True)
find_commit_thread.start()


def make_sender(pathy, directy):
    """
    Generate a file sender function.

    Args:
        pathy: The path of it.
        directy: The directory of it.

    Returns:
        The sender function.
    """

    def sender_function():
        mimetype = mimetypes.guess_type(pathy)[0]
        return send_from_directory(
            os.path.join(app.root_path, "game/" + directy),
            pathy.replace("/", ""),
            mimetype=mimetype,
        )

    return sender_function


def walk():
    """
    Walk the game folder files, and return a 2D list.

    Returns:
        A list of files, something like this:
        [["related/", "play.css"],
        ["related/", "welcome.css"],
        ["fonts/", "open-sans.ttf"]]
    """
    pys = []
    for root, _dirs, files in os.walk("game"):
        for file_name in files:
            if "html" not in file_name:
                pys.append([root.replace("game/", ""), f"/{file_name}"])
    return pys


def has_no_empty_params(rule):
    """
    Check whether a flask rule has no empty paramaters.

    Args:
        rule: The rule to check.

    Returns:
        True or False.
    """
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def track_view(page, ip_addr, agent):
    """
    Send a web request to Google Analytics to track a page view.

    Args:
        page: The URL for it.
        ip_addr: The IP of the user.
        agent: The user agent of the user.
    """
    tracking_data = {
        "v": "1",
        "tid": "UA-165004437-2",
        "cid": hashlib.sha512((str(ip_addr) + str(agent)).encode()).hexdigest(),
        "t": "pageview",
        "dh": "tank-scorecard.herokuapp.com",
        "dp": quote(page),
        "npa": "1",
        "ds": "server",
        "z": str(randint(0, pow(10, 10))),
    }
    if ip_addr is not None:
        tracking_data["uip"] = ip_addr
    if agent is not None:
        tracking_data["ua"] = quote(agent)
    requests.post(
        "https://www.google-analytics.com/collect", data=tracking_data
    )


@app.before_request
def before_req():
    """
    Goes to HTTPS, does stuff with user-agent, and tracks time.

    Returns:
        None usually, but if it's HTTP, it returns a redirect to HTTPS.
    """
    if "debug_mode_enabled" not in globals():
        now_in_ms = time.time() * 1000
        flask_global.before_before_request_time = now_in_ms
        flask_global.middle_before_request_time = now_in_ms
        flask_global.after_before_request_time = now_in_ms
        flask_global.after_after_request_time = now_in_ms
        if request.headers["X-Forwarded-Proto"] == "http":
            return redirect(request.url.replace("http", "https"), code=301)
        user_agent = None
        ua_add = ""
        if "User-Agent" in request.headers:
            user_agent = request.headers["User-Agent"]
            ua_add = ", " + str(ua_parse(user_agent))
        ip_addr = request.headers["X-Forwarded-For"]
        print("Hit from " + ip_addr + ua_add)
        chunks = request.url.split("/")
        flask_global.middle_before_request_time = now_in_ms
        track_view("/".join(chunks[2 : len(chunks)]), ip_addr, user_agent)
        flask_global.after_before_request_time = now_in_ms


@app.after_request
def after_req(response):
    """
    Do some final tweaks to the request before it gets sent.

    Args:
        response: The response to modify.

    Returns:
        The modified response.
    """
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
    if "debug_mode_enabled" not in globals():
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
    """
    Render the home page.

    Returns:
        HTML home page.
    """
    return render_template("welcome.html")


# card
@app.route("/cluecard/<theid>")
def card(theid):
    """
    Render the cluecard.

    Args:
        theid: ID of the user.

    Returns:
        HTML clue card.
    """
    return render_template("play.html", uid=theid)


# 404
@app.errorhandler(404)
def err404(_error):
    """
    Render the 404 error page.

    Returns:
        HTML page for when a page isn't found.
    """
    if request.url[len(request.url) - 1] == "/":
        return redirect(request.url[: len(request.url) - 1], code=301)
    return render_template("404.html"), 404


@app.route("/404")
def ex404():
    """
    Render the 404 error page, for the service worker.

    Returns:
        HTML page for when a page isn't found.
    """
    return render_template("404.html")


# 500
@app.errorhandler(500)
def err500(_error):
    """
    Render the 500 error page.

    Returns:
        HTML page for when there's an exception.
    """
    return render_template("500.html"), 500


# ============== API ================
@app.route("/makeid/<username>")
def genew_id(username):
    """
    Create an ID for a user.

    Args:
        username: Username for the user.

    Returns:
        Where to redirect to with the ID.
    """
    username = username.lower()
    try:
        id_database = json.load(open("ids.db", "r"))
    except FileNotFoundError:
        id_database = {}
    new_id = str(randint(0, 99999)).zfill(5)
    if username in id_database:
        old_id = id_database[username]
        try:
            group_database = json.load(open("groups.db", "r"))
        except FileNotFoundError:
            group_database = []
        for group in group_database:
            group_database[group_database.index(group)] = [
                new_id if user_id == old_id else user_id for user_id in group
            ]
        print(group_database)
        json.dump(group_database, open("groups.db", "w"))
    # First ID
    id_database[username] = new_id
    print(id_database)
    json.dump(id_database, open("ids.db", "w"))
    return f"/cluecard/{id_database[username]}"


@app.route("/addid/<exist>/<new>")
def addid(exist, new):
    """
    Group mechanic: Add two IDs together.

    Args:
        exist: The ID that's sending the add request.
        new: The ID to be added on.

    Returns:
        Whether it worked, and if it worked, what happened in order to merge.
    """
    exist = exist.zfill(5)
    new = new.zfill(5)
    try:
        aids = list(json.load(open("ids.db", "r")).values())
    except Exception:
        aids = []
    if exist not in aids or new not in aids:
        try:
            json.load(open("ids.db", "r"))
        except Exception:
            json.dump({}, open("ids.db", "w"))
        print(f"{exist} or {new} are not in {aids}")
        print(f'exist {"is" if exist in aids else "is not"} in ids')
        print(f'new {"is" if new in aids else "is not"} in ids')
        return "notreal"
    try:
        group_database = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        group_database = []
    comp = [user_id for group in group_database for user_id in group]
    for group in group_database:
        if exist in group and new in group:
            return "already"
    if exist in comp and new in comp:
        newgp = []
        for group in group_database:
            if new in group:
                newgp = group
        for group in group_database:
            if exist in group:
                group_database[group_database.index(group)] = (
                    group + newgp[1 : len(newgp)]
                )
                group_database.remove(newgp)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "merge"
    elif exist in comp and new not in comp:
        for group in group_database:
            if exist in group:
                group_database[group_database.index(group)].append(new)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "addnew"
    elif exist not in comp and new in comp:
        for group in group_database:
            if new in group:
                group_database[group_database.index(group)].append(exist)
                print(group_database)
                json.dump(group_database, open("groups.db", "w"))
                return "addexist"
    else:
        # The best make you win, most tell you what it's not,
        # and some don't give you anything.
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
    """
    Find all people in a group.

    Args:
        uid: The user ID.

    Returns:
        A HTML string for which people are in the group.
    """
    try:
        group_database = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        group_database = []
    try:
        done_database = json.load(open("done.db", "r"))
    except FileNotFoundError:
        done_database = {}
    comp = [user_id for group in group_database for user_id in group]
    if uid not in comp:
        return "You currently don't have anyone in your group."
    for group in group_database:
        if uid in group:
            try:
                id_database = json.load(open("ids.db", "r"))
            except FileNotFoundError:
                id_database = {}
            group = group[1 : len(group)]
            inv_map = {user_id: name for name, user_id in id_database.items()}
            mgroup = [
                inv_map[person] + done_database.get(person, "")
                for person in group.copy()
            ]
            return (
                "In your group, there's these people: "
                + f'<span style="color: deepskyblue;">{", ".join(mgroup)}</span>'
            )


@app.route("/cardstatus/<uid>/<cardnum>")
def checkcard(uid, cardnum):
    """
    Check a card number for a user ID.

    Args:
        uid: The user ID.
        cardnum: The card ID.

    Returns:
        0 if the card is right.
        1 if it should give the player a hint.
        2 if it's not a helpful card.
    """
    try:
        group_database = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        group_database = []
    comp = [user_id for group in group_database for user_id in group]
    if uid not in comp:
        return "invalid"
    for group in group_database:
        if uid in group:
            if cardnum in group[0]:
                return group[0][cardnum]
            return "invalid"


@app.route("/rightnum/<uid>")
def rightnum(uid):
    """
    Find the right number based on a user ID.

    Args:
        uid: The user ID.

    Returns:
        The correct number for that ID.
    """
    try:
        group_database = json.load(open("groups.db", "r"))
    except FileNotFoundError:
        group_database = []
    comp = [user_id for group in group_database for user_id in group]
    if uid not in comp:
        return "-1"
    for group in group_database:
        if uid in group:
            return group[0]["rightnum"]


@app.route("/finished/<user_id>")
def send_finished(user_id):
    """
    Add a user ID to the finished database.

    Args:
        user_id: The user ID to be added.

    Returns:
        "done" and the current database.
    """
    try:
        done_database = json.load(open("done.db", "r"))
    except FileNotFoundError:
        done_database = {}
    if user_id not in done_database:
        done_database[user_id] = " (🏁 finished)"
    json.dump(done_database, open("done.db", "w"))
    return f"done {done_database}"


# ========== BROWSER FILES ==========
for folder_name, file_name in walk():
    if file_name != "/sw.js":
        app.add_url_rule(
            file_name,
            file_name,
            make_sender(file_name, folder_name),
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
    service_worker = render_template(
        "browserfiles/sw.js", urls=swlist, version=str(comm_num)
    )
    response = app.make_response(service_worker)
    response.mimetype = "application/javascript"
    return response
