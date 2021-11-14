import os

import flask
import requests
from flask import request

from randomiser import daily, utils
from randomiser.database import manager
from randomiser.endpoints import _format_time

VERIFICATION_WEBHOOK = os.environ["VERIFICATION_WEBHOOK"]
VERIFICATION_TOKEN = os.environ["VERIFICATION_TOKEN"]

bp = flask.Blueprint("api", __name__, url_prefix="/api")


@bp.route("/random_player_loadout")
def random_player_loadout():
    rundown_id = int(request.args["rundown_id"])
    return utils.loadout_to_json(utils.get_random_loadout(rundown_id))


@bp.route("/random_stage")
def random_stage():
    rundown_id = int(request.args["rundown_id"])
    return utils.stage_to_json(utils.get_random_stage(rundown_id))


@bp.route("/random_full_loadout")
def random_full_loadout():
    rundown_id = int(request.args["rundown_id"])
    return {
        "players": {
            "1": utils.loadout_to_json(utils.get_random_loadout(rundown_id)),
            "2": utils.loadout_to_json(utils.get_random_loadout(rundown_id)),
            "3": utils.loadout_to_json(utils.get_random_loadout(rundown_id)),
            "4": utils.loadout_to_json(utils.get_random_loadout(rundown_id)),
        },
        "stage": utils.stage_to_json(utils.get_random_stage(rundown_id)),
    }


@bp.route("/submit_daily", methods=["POST"])
def submit_daily_run():
    discord_uid = request.cookies["gr_d_uid"]
    hrs = int(request.form["hours"])
    mins = int(request.form["minutes"])
    secs = int(request.form["seconds"])
    evidence_url = request.form["url"]

    total_seconds = (hrs * 3600) + (mins * 60) + secs

    dbm = manager.get_database_manager()
    run_id = dbm.create_daily_submission(discord_uid, total_seconds, evidence_url)

    requests.post(
        VERIFICATION_WEBHOOK,
        json={
            "content": "<@&823030353551818752>",
            "embeds": [
                {
                    "title": "New run submitted",
                    "description": f"**Run length:** `{_format_time(total_seconds)}`\n**Evidence:** [Click]({evidence_url})\n**Submitted By:** <@{discord_uid}> (`{discord_uid}`)\n\n**ID:** `{run_id}`",
                }
            ],
        },
    )

    return flask.redirect(flask.url_for("endpoints.daily"))


@bp.route("/verify_daily_run", methods=["POST"])
def verify_daily_run():
    if request.headers["Authorisation"] != VERIFICATION_TOKEN:
        return flask.Response(status=403)

    dbm = manager.get_database_manager()
    dbm.verify_run(int(request.args["run_id"]))

    return flask.Response(status=200)


@bp.route("/reject_daily_run", methods=["POST"])
def reject_daily_run():
    if request.headers["Authorisation"] != VERIFICATION_TOKEN:
        return flask.Response(status=403)

    dbm = manager.get_database_manager()
    dbm.delete_run(int(request.args["run_id"]))

    return flask.Response(status=200)


@bp.route("/daily")
def get_daily():
    loadout = daily.get_daily()

    def _create_p_dict(p):
        return {
            "primary": str(p[0]),
            "secondary": str(p[1]),
            "tool": str(p[2]),
            "melee": str(p[3]),
        }

    return {
        "players": {
            "1": _create_p_dict(loadout["p1"]),
            "2": _create_p_dict(loadout["p1"]),
            "3": _create_p_dict(loadout["p1"]),
            "4": _create_p_dict(loadout["p1"]),
        },
        "stage": {
            "stage": str(loadout["stage"][0]),
            "difficulty": str(loadout["stage"][1]),
        },
    }


def setup(app: flask.Flask) -> None:
    app.register_blueprint(bp)
