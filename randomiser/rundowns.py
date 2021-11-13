import dataclasses
import random
import typing

from randomiser.enums import difficulties, melees, primaries, secondaries, stages, tools


@dataclasses.dataclass
class RundownLoadoutInfo:
    id: int
    stages: typing.Sequence[stages.Stages]
    primaries: typing.Sequence[primaries.Primaries]
    secondaries: typing.Sequence[secondaries.Secondaries]
    tools: typing.Sequence[tools.Tools]
    melees: typing.Sequence[melees.Melees]
    difficulties: typing.Mapping[str, typing.Sequence[difficulties.Difficulties]]

    def get_random_stage(self):
        return random.choice(self.stages)

    def get_random_primary(self):
        return random.choice(self.primaries)

    def get_random_secondary(self):
        return random.choice(self.secondaries)

    def get_random_tool(self):
        return random.choice(self.tools)

    def get_random_melee(self):
        return random.choice(self.melees)

    def get_random_difficulty(self, stage):
        return random.choice(self.difficulties[stage])

    @classmethod
    def from_json(cls, json_data):
        return cls(
            json_data["id"],
            [stages.Stages(s) for s in json_data["stages"]],
            [primaries.Primaries(p) for p in json_data["primaries"]],
            [secondaries.Secondaries(s) for s in json_data["secondaries"]],
            [tools.Tools(u) for u in json_data["tools"]],
            [melees.Melees(m) for m in json_data["melees"]],
            {
                k: [difficulties.Difficulties(d) for d in v]
                for k, v in json_data["difficulties"].items()
            },
        )
