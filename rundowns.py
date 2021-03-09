import dataclasses
import typing
import random
import json

import enums


@dataclasses.dataclass
class RundownLoadoutInfo:
    id: int
    stages: typing.Sequence[enums.Stage]
    primaries: typing.Sequence[enums.Primary]
    specials: typing.Sequence[enums.Special]
    utility: typing.Sequence[enums.Utility]
    melees: typing.Sequence[enums.Melee]
    difficulties: typing.Mapping[str, typing.Sequence[enums.Difficulty]]

    def get_random_stage(self):
        return random.choice(self.stages)

    def get_random_primary(self):
        return random.choice(self.primaries)

    def get_random_special(self):
        return random.choice(self.specials)

    def get_random_utility(self):
        return random.choice(self.utility)

    def get_random_melee(self):
        return random.choice(self.melees)

    def get_random_difficulty(self, stage):
        return random.choice(self.difficulties[stage])

    @classmethod
    def from_json(cls, json_data):
        return cls(
            json_data["id"],
            [enums.Stage(s) for s in json_data["stages"]],
            [enums.Primary(p) for p in json_data["primaries"]],
            [enums.Special(s) for s in json_data["specials"]],
            [enums.Utility(u) for u in json_data["utilities"]],
            [enums.Melee(m) for m in json_data["melees"]],
            {k: [enums.Difficulty(d) for d in v] for k, v in json_data["difficulties"].items()},
        )


def load_rundown_info(config: typing.Mapping[str, typing.Any]) -> typing.Mapping[int, RundownLoadoutInfo]:
    rundowns = {}
    for rundown_file in config["rundown_info_files"]:
        with open(rundown_file) as fp:
            data = json.load(fp)
        rundown = RundownLoadoutInfo.from_json(data)
        rundowns[rundown.id] = rundown
    return rundowns
