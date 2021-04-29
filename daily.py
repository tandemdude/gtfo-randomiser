import datetime
import enums
import time

from psycopg2 import OperationalError

import utils

RUNDOWNS = utils.get_rundown_data()
CURRENT_RUNDOWN = 5


def create_daily(conn, current_rundown):
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    p1 = ",".join(str(i.value) for i in utils.get_random_loadout(current_rundown))
    p2 = ",".join(str(i.value) for i in utils.get_random_loadout(current_rundown))
    p3 = ",".join(str(i.value) for i in utils.get_random_loadout(current_rundown))
    p4 = ",".join(str(i.value) for i in utils.get_random_loadout(current_rundown))
    stage = ",".join(str(i.value) for i in utils.get_random_stage(current_rundown))

    conn.execute(
        "INSERT INTO daily(loadout_date, player1, player2, player3, player4, stage) VALUES(%s, %s, %s, %s, %s, %s);",
        (date, p1, p2, p3, p4, stage)
    )

    return p1, p2, p3, p4, stage


def db_out_to_enums(db_result):
    p1_raw = db_result[0].split(",")
    p1 = (enums.Primary(int(p1_raw[0])), enums.Special(int(p1_raw[1])), enums.Utility(int(p1_raw[2])), enums.Melee(int(p1_raw[3])))
    p2_raw = db_result[1].split(",")
    p2 = (enums.Primary(int(p2_raw[0])), enums.Special(int(p2_raw[1])), enums.Utility(int(p2_raw[2])), enums.Melee(int(p2_raw[3])))
    p3_raw = db_result[2].split(",")
    p3 = (enums.Primary(int(p3_raw[0])), enums.Special(int(p3_raw[1])), enums.Utility(int(p3_raw[2])), enums.Melee(int(p3_raw[3])))
    p4_raw = db_result[3].split(",")
    p4 = (enums.Primary(int(p4_raw[0])), enums.Special(int(p4_raw[1])), enums.Utility(int(p4_raw[2])), enums.Melee(int(p4_raw[3])))
    stage_raw = db_result[4].split(",")
    stage = enums.Stage(int(stage_raw[0])), enums.Difficulty(int(stage_raw[1]))
    return {"players": [p1, p2, p3, p4], "stage": stage}


def get_daily(pool, date=None):
    date = date or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    with utils.acquire_conn(pool) as conn:
        daily = conn.fetchone("SELECT player1, player2, player3, player4, stage FROM daily WHERE loadout_date = %s;", (date,))
        if daily is None:
            daily = create_daily(conn, CURRENT_RUNDOWN)
    return db_out_to_enums(daily)


def _seconds_to_time_string(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}"


def get_daily_runs(pool):
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    with utils.acquire_conn(pool) as conn:
        rows = conn.fetch("SELECT run_id, run_time, evidence_url, run_verified FROM daily_runs WHERE run_date = %s ORDER BY run_time ASC LIMIT 20;", (date,))
        if not rows:
            return [(1, "No Data", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Yes", "No Data")]
    return [(i, _seconds_to_time_string(row[1]), row[2], "Yes" if row[3] else "No", row[0]) for i, row in enumerate(rows, start=1)]


def add_daily_run(pool, time_str, evidence_url):
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    h, m, s = time_str.split(":")
    total_seconds = (int(h) * 60 * 60) + (int(m) * 60) + int(s)

    with utils.acquire_conn(pool) as conn:
        run_id = conn.fetchone("INSERT INTO daily_runs(run_date, run_time, evidence_url) VALUES(%s, %s, %s) RETURNING run_id;", (date, total_seconds, evidence_url))
    return run_id[0]


def verify_daily(pool, run_id):
    with utils.acquire_conn(pool) as conn:
        conn.execute("UPDATE daily_runs SET run_verified = %s WHERE run_id = %s;", (True, run_id))


def reject_daily(pool, run_id):
    with utils.acquire_conn(pool) as conn:
        conn.execute("DELETE FROM daily_runs WHERE run_id = %s", (run_id,))


def get_previous_leaderboard(pool, date):
    with utils.acquire_conn(pool) as conn:
        rows = conn.fetch("SELECT run_id, run_time, evidence_url, run_verified FROM daily_runs WHERE run_date = %s ORDER BY run_time ASC LIMIT 20;", (date,))
        if not rows:
            return [(1, "No Data", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Yes", "No Data")]
    return [(i, _seconds_to_time_string(row[1]), row[2], "Yes" if row[3] else "No", row[0]) for i, row in enumerate(rows, start=1)]


def get_previous_daily_dates(pool):
    with utils.acquire_conn(pool) as conn:
        rows = conn.fetch("SELECT DISTINCT run_date FROM daily_runs;")
        if not rows:
            return [datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")]
    return [row[0] for row in rows]


def get_daily_data(POOL, extra_data=None):
    success = False
    for _ in range(5):
        try:
            d = get_daily(POOL)
            runs = get_daily_runs(POOL)
            success = True
            break
        except OperationalError:
            time.sleep(0.2)
            continue

    if not success:
        return False

    players = enumerate(
        [(("Primary:", str(p[0])), ("Special:", str(p[1])), ("Utility:", str(p[2])), ("Melee:", str(p[3]))) for p in
         d["players"]],
        start=1
    )
    if extra_data is None:
        return players, d["stage"][0], d["stage"][1], runs, get_previous_daily_dates(POOL)

    prev_runs = get_previous_leaderboard(POOL, extra_data)
    return players, d["stage"][0], d["stage"][1], runs, get_previous_daily_dates(POOL), prev_runs
