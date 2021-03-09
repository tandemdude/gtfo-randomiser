import json

import flask
from flask import request

import rundowns

app = flask.Flask(__name__)

with open("config.json") as fp:
    CONFIG = json.load(fp)
RUNDOWNS = rundowns.load_rundown_info(CONFIG)

EMPTY_CARD = [("Primary:", "..."), ("Special:", "..."), ("Utility:", "..."), ("Melee:", "...")]
PLAYERS = [1, 2, 3, 4]


def get_random_loadout(rundown_id):
    return {
        "primary": RUNDOWNS[rundown_id].get_random_primary(),
        "special": RUNDOWNS[rundown_id].get_random_special(),
        "utility": RUNDOWNS[rundown_id].get_random_utility(),
        "melee": RUNDOWNS[rundown_id].get_random_melee()
    }


@app.route("/")
def index():
    return flask.render_template(
        "index.html",
        player_card_default_data=EMPTY_CARD,
        players=PLAYERS,
        rundown_ids=[r.id for r in RUNDOWNS.values()]
    )


@app.route("/api/random_player_loadout")
def random_player_loadout():
    rundown_id = int(request.args["rundown_id"])
    return get_random_loadout(rundown_id)


@app.route("/api/random_stage")
def random_stage():
    rundown_id = int(request.args["rundown_id"])
    stage = RUNDOWNS[rundown_id].get_random_stage()
    return {
        "stage": stage,
        "difficulty": RUNDOWNS[rundown_id].get_random_difficulty(stage)
    }


@app.route("/api/random_full_loadout")
def random_full_loadout():
    rundown_id = int(request.args["rundown_id"])
    stage = RUNDOWNS[rundown_id].get_random_stage()
    return {
        "1": get_random_loadout(rundown_id),
        "2": get_random_loadout(rundown_id),
        "3": get_random_loadout(rundown_id),
        "4": get_random_loadout(rundown_id),
        "stage": {
            "stage": stage,
            "difficulty": RUNDOWNS[rundown_id].get_random_difficulty(stage)
        }
    }
