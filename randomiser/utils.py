import json
from importlib import resources

from randomiser import rundown_data, rundowns


def _load_rundown(rundown_id: int) -> rundowns.RundownLoadoutInfo:
    data = resources.read_text(rundown_data, f"rundown_{rundown_id}.json")
    return rundowns.RundownLoadoutInfo.from_json(json.loads(data))


def get_random_loadout(rundown_id: int):
    _rundown = _load_rundown(rundown_id)
    return (
        _rundown.get_random_primary(),
        _rundown.get_random_secondary(),
        _rundown.get_random_tool(),
        _rundown.get_random_melee(),
    )


def loadout_to_json(loadout):
    return {
        "primary": str(loadout[0]),
        "secondary": str(loadout[1]),
        "tool": str(loadout[2]),
        "melee": str(loadout[3]),
    }


def get_random_stage(rundown_id):
    _rundown = _load_rundown(rundown_id)
    stage = _rundown.get_random_stage()
    difficulty = _rundown.get_random_difficulty(str(stage))
    return stage, difficulty


def stage_to_json(stage):
    return {"stage": str(stage[0]), "difficulty": str(stage[1])}
