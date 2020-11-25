"""This is the scorecard Heroku app. Look at the README for more details."""

# ============== INIT ==============

# General stuff
import mimetypes
import os
from random import randint
import time
import json

from flask import (
    Flask,
    g as flask_global,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from api_app import app as api_app
from github.MainClass import Github

# Tracking
import hashlib
from urllib.parse import quote
import requests

# Service worker
import threading

# Tests
import __main__

debug_mode = "boot" in __main__.__file__

if debug_mode:
    id_database = open("ids.db", "w")
    id_database.write(
        """
    {
    "test": "12345"
    }
    """
    )
    id_database.close()
# Minfication

compress_inited = True
try:
    from flask_compress import Compress
except ModuleNotFoundError:
    compress_inited = False
minify_inited = True
try:
    from flask_minify import minify
except ModuleNotFoundError:
    minify_inited = False

# Init flask
app = Flask(__name__, template_folder="game")
if compress_inited:
    Compress(app)
if minify_inited:
    minify(app=app, js=False, fail_safe=False, caching_limit=0)
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
if not debug_mode:
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
                pys.append(
                    [root.replace("\\", "/").replace("game/", ""), f"/{file_name}"]
                )
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
    requests.post("https://www.google-analytics.com/collect", data=tracking_data)


@app.before_request
def before_req():
    """
    Goes to HTTPS, does stuff with user-agent, and tracks time.

    Returns:
        None usually, but if it's HTTP, it returns a redirect to HTTPS.
    """
    # Use Host to determine if in prod
    if not debug_mode:
        now_in_ms = time.time() * 1000
        flask_global.before_before_request_time = now_in_ms
        flask_global.middle_before_request_time = now_in_ms
        flask_global.after_before_request_time = now_in_ms
        flask_global.after_after_request_time = now_in_ms
        if request.headers["X-Forwarded-Proto"] == "http":
            return redirect(request.url.replace("http", "https"), code=301)
        user_agent = None
        if "User-Agent" in request.headers:
            user_agent = request.headers["User-Agent"]
        ip_addr = request.headers["X-Forwarded-For"]
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
    if not debug_mode:
        response.headers["Content-Security-Policy"] = (
            "default-src https: 'unsafe-eval' 'unsafe-inline'; object-src 'none';"
            + "worker-src blob: 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'"
        )
    if response.status_code != 301:
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if not debug_mode:
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
        flask_global.after_after_request_time = time.time() * 1000
        server_timing += ', process;desc="Render stuff";dur='
        server_timing += str(
            round(
                flask_global.after_after_request_time
                - flask_global.after_before_request_time,
                1,
            )
        )
        server_timing += ', process;desc="Total server-side timing";dur='
        server_timing += str(
            round(
                flask_global.after_after_request_time
                - flask_global.before_before_request_time,
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
@app.route("/cluecard/<username>")
def card(username):
    """
    Render the cluecard.

    Args:
        username: Username.

    Returns:
        HTML clue card.
    """
    try:
        id_database = json.load(open("ids.db"))
    except FileNotFoundError:
        id_database = {}
    if username in id_database:
        return render_template(
            "play.html", uid=id_database[username], username=username
        )
    return render_template("404.html"), 404


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
app.register_blueprint(api_app, url_prefix="/api/")
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
            if "debug" not in url and "eslint" not in url:
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
