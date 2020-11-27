from app import app, debug_mode


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
