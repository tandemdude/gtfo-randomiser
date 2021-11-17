import datetime
import logging

import flask
from flask import request, session

from randomiser import auth
from randomiser import daily as daily_
from randomiser.database import manager

_LOGGER = logging.getLogger("randomiser.endpoints")
bp = flask.Blueprint("endpoints", __name__)

DEFAULT_DAILY_ROW = [
    "No Data",
    0,
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "Yes",
    "No Data",
]


def _format_time(n_seconds):
    m, s = divmod(n_seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}"


@bp.route("/index")
@bp.route("/")
def root():
    auth_success = {"fail": False, "success": True}[request.args.get("auth", "fail")]
    if session.get("gr_d_uid"):
        auth_success = True
    return flask.render_template(
        "index.html",
        auth_success=auth_success,
        handicap="Play the entire stage on 20% hp only",
    )


@bp.route("/daily")
def daily():
    authed = session.get("gr_d_uid") is not None

    daily_loadout = daily_.get_daily()

    dbm = manager.get_database_manager()
    now = datetime.datetime.now(datetime.timezone.utc).date()
    todays_runs = dbm.get_top_ten_daily_runs(now.strftime("%Y-%m-%d"))
    if not todays_runs:
        todays_runs = [DEFAULT_DAILY_ROW]

    for i in range(len(todays_runs)):
        todays_runs[i] = list(todays_runs[i])
        todays_runs[i][1] = _format_time(todays_runs[i][1])

    yesterday_winner = dbm.get_daily_winner(
        (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    )
    yesterday_winner = list(yesterday_winner or ()) or [
        "No Winner :(",
        0,
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "69420",
    ]
    yesterday_winner[1] = _format_time(yesterday_winner[1])

    return flask.render_template(
        "daily.html",
        auth_success=authed,
        submitted_runs=todays_runs,
        d=daily_loadout,
        str=str,
        yesterday_winner=yesterday_winner,
    )


@bp.route("/profile")
def profile():
    user_id = session.get("gr_d_uid")
    if user_id is None:
        return flask.redirect(flask.url_for(".root"))

    dbm = manager.get_database_manager()
    user = dbm.get_username_and_discrim(user_id)

    daily_runs = dbm.get_daily_runs_for_user(user_id) or [DEFAULT_DAILY_ROW]
    for i in range(len(daily_runs)):
        daily_runs[i] = list(daily_runs[i])
        daily_runs[i][1] = _format_time(daily_runs[i][1])

    return flask.render_template("profile.html", user=user, submitted_runs=daily_runs)


@bp.route("/login")
def login():
    url, state = auth.get_auth_url()

    dbm = manager.get_database_manager()
    dbm.save_state(state)

    return flask.redirect(url)


@bp.route("/logout")
def logout():
    session.pop("gr_d_uid", None)
    return flask.make_response(flask.render_template("logout.html"))


@bp.route("/authCallback")
def complete_auth():
    dbm = manager.get_database_manager()
    state = dbm.validate_state(request.args.get("state"))
    dbm.delete_state(state)

    if (
        request.args.get("error") == "access_denied"
        or not request.args.get("code")
        or not state
    ):
        return flask.redirect(flask.url_for(".root", auth="fail"))

    user_info, tokens = auth.exchange_code(request)
    dbm.delete_tokens_for_same_user(user_info["id"])
    dbm.save_tokens(
        user_info["id"], user_info["username"], user_info["discriminator"], tokens
    )

    session["gr_d_uid"] = user_info["id"]
    return flask.redirect(flask.url_for(".root", auth="success"))


def setup(app: flask.Flask) -> None:
    app.register_blueprint(bp)
