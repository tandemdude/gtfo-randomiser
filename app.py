import os
import time

import requests
import flask
from flask import request, Response
from psycopg2 import pool
from psycopg2 import OperationalError

import utils
import daily as daily_

app = flask.Flask(__name__)
POOL = pool.ThreadedConnectionPool(3, 10, os.environ["DATABASE_URL"])
utils.init_db(POOL)

RUNDOWNS = utils.get_rundown_data()

EMPTY_CARD = [("Primary:", "..."), ("Special:", "..."), ("Utility:", "..."), ("Melee:", "...")]
PLAYERS = [1, 2, 3, 4]
VERIFICATION_WEBHOOK = os.environ["VERIFICATION_WEBHOOK"]
VERIFICATION_TOKEN = os.environ["VERIFICATION_TOKEN"]


@app.route("/")
def index():
    return flask.render_template(
        "index.html",
        player_card_default_data=EMPTY_CARD,
        players=PLAYERS,
        rundown_ids=[r.id for r in RUNDOWNS.values()]
    )


@app.route("/daily")
def daily():
    success = False
    for _ in range(5):
        try:
            d = daily_.get_daily(POOL)
            runs = daily_.get_daily_runs(POOL)
            success = True
            break
        except OperationalError:
            time.sleep(0.2)
            continue

    if not success:
        return flask.render_template("error.html")

    players = enumerate(
        [(("Primary:", str(p[0])), ("Special:", str(p[1])), ("Utility:", str(p[2])), ("Melee:", str(p[3]))) for p in d["players"]],
        start=1
    )
    return flask.render_template("daily.html", players=players, stage=d["stage"][0], difficulty=d["stage"][1], runs_data=runs)


@app.route("/api/submit_daily", methods=["POST"])
def submit_daily():
    hours, minutes, seconds = request.form["hours"], request.form["minutes"], request.form["seconds"]
    evidence = request.form["imagelink"]
    time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    run_id = daily_.add_daily_run(POOL, time_str, evidence)
    requests.post(
        VERIFICATION_WEBHOOK,
        json={
            "content": "<@&823030353551818752>",
            "embeds": [
                {
                    "title": "New run submitted",
                    "description": f"**Run length:** `{time_str}`\n**Evidence:** [Click]({evidence})\n\n**ID:** `{run_id}`"
                }
            ]
        }
    )
    return flask.redirect(flask.url_for("daily"))


@app.route("/api/verify_daily_run", methods=["POST"])
def verify_daily_run():
    if request.headers["Authorisation"] != VERIFICATION_TOKEN:
        return Response(status=403)

    daily_.verify_daily(POOL, int(request.args["run_id"]))

    return Response(status=200)


@app.route("/api/reject_daily_run", methods=["POST"])
def reject_daily_run():
    if request.headers["Authorisation"] != VERIFICATION_TOKEN:
        return Response(status=403)

    daily_.reject_daily(POOL, int(request.args["run_id"]))

    return Response(status=200)


@app.route("/api/random_player_loadout")
def random_player_loadout():
    rundown_id = int(request.args["rundown_id"])
    return utils.loadout_to_json(utils.get_random_loadout(rundown_id))


@app.route("/api/random_stage")
def random_stage():
    rundown_id = int(request.args["rundown_id"])
    return utils.stage_to_json(utils.get_random_stage(rundown_id))


@app.route("/api/random_full_loadout")
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


@app.route("/api/daily")
def get_daily_loadout():
    success = False
    for _ in range(5):
        try:
            d = daily_.get_daily(POOL)
            success = True
            break
        except OperationalError:
            time.sleep(0.2)
            continue

    if not success:
        return Response(status=500)

    return {
        "players": {
            "1": utils.loadout_to_json(d["players"][0]),
            "2": utils.loadout_to_json(d["players"][1]),
            "3": utils.loadout_to_json(d["players"][2]),
            "4": utils.loadout_to_json(d["players"][3]),
        },
        "stage": utils.stage_to_json(d["stage"]),
    }
