import datetime

from randomiser import utils
from randomiser.database import manager
from randomiser.enums import difficulties, melees, primaries, secondaries, stages, tools

CURRENT_RUNDOWN = 6


def create_daily(current_rundown):
    date = datetime.datetime.now(datetime.timezone.utc).date().strftime("%Y-%m-%d")

    p1 = ",".join(str(i.value) for i in utils.get_random_loadout(current_rundown))
    p2 = ",".join(str(i.value) for i in utils.get_random_loadout(current_rundown))
    p3 = ",".join(str(i.value) for i in utils.get_random_loadout(current_rundown))
    p4 = ",".join(str(i.value) for i in utils.get_random_loadout(current_rundown))
    stage = ",".join(str(i.value) for i in utils.get_random_stage(current_rundown))

    dbm = manager.get_database_manager()
    dbm.save_daily_run(date, p1, p2, p3, p4, stage)

    return p1, p2, p3, p4, stage


def get_daily():
    dbm = manager.get_database_manager()
    db_result = dbm.get_daily(
        datetime.datetime.now(datetime.timezone.utc).date().strftime("%Y-%m-%d")
    )
    if not db_result:
        db_result = create_daily(5)

    p1_raw = db_result[0].split(",")
    p1 = (
        primaries.Primaries(int(p1_raw[0])),
        secondaries.Secondaries(int(p1_raw[1])),
        tools.Tools(int(p1_raw[2])),
        melees.Melees(int(p1_raw[3])),
    )
    p2_raw = db_result[1].split(",")
    p2 = (
        primaries.Primaries(int(p2_raw[0])),
        secondaries.Secondaries(int(p2_raw[1])),
        tools.Tools(int(p2_raw[2])),
        melees.Melees(int(p2_raw[3])),
    )
    p3_raw = db_result[2].split(",")
    p3 = (
        primaries.Primaries(int(p3_raw[0])),
        secondaries.Secondaries(int(p3_raw[1])),
        tools.Tools(int(p3_raw[2])),
        melees.Melees(int(p3_raw[3])),
    )
    p4_raw = db_result[3].split(",")
    p4 = (
        primaries.Primaries(int(p4_raw[0])),
        secondaries.Secondaries(int(p4_raw[1])),
        tools.Tools(int(p4_raw[2])),
        melees.Melees(int(p4_raw[3])),
    )
    stage_raw = db_result[4].split(",")
    stage = stages.Stages(int(stage_raw[0])), difficulties.Difficulties(
        int(stage_raw[1])
    )
    return {"p1": p1, "p2": p2, "p3": p3, "p4": p4, "stage": stage}
