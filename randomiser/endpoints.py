import datetime
import logging

import flask
from flask import request

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
    if request.cookies.get("gr_d_uid"):
        auth_success = True
    return flask.render_template("index.html", auth_success=auth_success)


@bp.route("/daily")
def daily():
    authed = request.cookies.get("gr_d_uid") is not None

    daily_loadout = daily_.get_daily()

    dbm = manager.get_database_manager()
    todays_runs = dbm.get_top_ten_daily_runs(
        datetime.datetime.now(datetime.timezone.utc).date().strftime("%Y-%m-%d")
    )
    if not todays_runs:
        todays_runs = [DEFAULT_DAILY_ROW]

    for i in range(len(todays_runs)):
        todays_runs[i] = list(todays_runs[i])
        todays_runs[i][1] = _format_time(todays_runs[i][1])

    return flask.render_template(
        "daily.html",
        auth_success=authed,
        submitted_runs=todays_runs,
        d=daily_loadout,
        str=str,
    )


@bp.route("/login")
def login():
    return flask.redirect(auth.get_auth_url())


@bp.route("/authCallback")
def complete_auth():
    if request.args.get("error") == "access_denied" or not request.args.get("code"):
        return flask.redirect(flask.url_for(".root", auth="fail"))

    user_info, tokens = auth.exchange_code(request)
    dbm = manager.get_database_manager()
    dbm.delete_tokens_for_same_user(user_info["id"])
    dbm.save_tokens(
        user_info["id"], user_info["username"], user_info["discriminator"], tokens
    )

    redirect = flask.redirect(flask.url_for(".root", auth="success"))
    redirect.set_cookie("gr_d_uid", user_info["id"], max_age=60 * 60 * 24 * 365)
    return redirect


def setup(app: flask.Flask) -> None:
    app.register_blueprint(bp)
