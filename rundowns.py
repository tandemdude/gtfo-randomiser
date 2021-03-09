import dataclasses
import typing
import random
import json


@dataclasses.dataclass
class RundownLoadoutInfo:
    id: int
    stages: typing.Sequence[str]
    primaries: typing.Sequence[str]
    specials: typing.Sequence[str]
    utility: typing.Sequence[str]
    melees: typing.Sequence[str]
    difficulties: typing.Mapping[str, typing.Sequence[str]]

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
            json_data["stages"],
            json_data["primaries"],
            json_data["specials"],
            json_data["utilities"],
            json_data["melees"],
            json_data["difficulties"],
        )


def load_rundown_info(config: typing.Mapping[str, typing.Any]) -> typing.Mapping[int, RundownLoadoutInfo]:
    rundowns = {}
    for rundown_file in config["rundown_info_files"]:
        with open(rundown_file) as fp:
            data = json.load(fp)
        rundown = RundownLoadoutInfo.from_json(data)
        rundowns[rundown.id] = rundown
    return rundowns
