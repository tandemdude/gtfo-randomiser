import os
import time

import requests
import flask
from flask import request
from psycopg2 import pool
from psycopg2 import OperationalError

import utils
import daily as daily_

app = flask.Flask(__name__)
POOL = pool.ThreadedConnectionPool(3, 10, os.environ["DATABASE_URL"])

RUNDOWNS = utils.get_rundown_data()

EMPTY_CARD = [("Primary:", "..."), ("Special:", "..."), ("Utility:", "..."), ("Melee:", "...")]
PLAYERS = [1, 2, 3, 4]
VERIFICATION_WEBHOOK = os.environ["VERIFICATION_WEBHOOK"]


@app.before_first_request
def server_setup():
    utils.init_db(POOL)


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
            "embeds": [
                {
                    "title": "New run submitted",
                    "description": f"**Run length:** `{time_str}`\n**Evidence:** [Click]({evidence})\n\n**ID:** `{run_id}`"
                }
            ]
        }
    )


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
        "1": utils.loadout_to_json(utils.get_random_loadout(rundown_id)),
        "2": utils.loadout_to_json(utils.get_random_loadout(rundown_id)),
        "3": utils.loadout_to_json(utils.get_random_loadout(rundown_id)),
        "4": utils.loadout_to_json(utils.get_random_loadout(rundown_id)),
        "stage": utils.stage_to_json(utils.get_random_stage(rundown_id))
    }
