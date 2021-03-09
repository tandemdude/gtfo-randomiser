import contextlib
import functools
import json

import rundowns


class Connection:
    def __init__(self, conn):
        self._conn = conn

    def execute(self, query, args=None):
        with self._conn.cursor() as curs:
            if args is None:
                curs.execute(query)
            else:
                curs.execute(query, args)

    def fetch(self, query, args=None):
        with self._conn.cursor() as curs:
            if args is None:
                curs.execute(query)
            else:
                curs.execute(query, args)

            return curs.fetchall()

    def fetchone(self, query, args=None):
        with self._conn.cursor() as curs:
            if args is None:
                curs.execute(query)
            else:
                curs.execute(query, args)

            return curs.fetchone()


@contextlib.contextmanager
def acquire_conn(pool):
    conn = pool.getconn()
    try:
        yield Connection(conn)
    finally:
        pool.putconn(conn)


def init_db(pool):
    with open("schema.sql") as fp:
        schema = fp.read()

    with acquire_conn(pool) as conn:
        conn.execute(schema)


@functools.lru_cache(maxsize=None)
def get_rundown_data():
    with open("config.json") as fp:
        conf = json.load(fp)

    return rundowns.load_rundown_info(conf)


def get_random_loadout(rundown_id):
    _rundowns = get_rundown_data()
    return (
        _rundowns[rundown_id].get_random_primary(),
        _rundowns[rundown_id].get_random_special(),
        _rundowns[rundown_id].get_random_utility(),
        _rundowns[rundown_id].get_random_melee()
    )


def loadout_to_json(loadout):
    return {
        "primary": str(loadout[0]),
        "special": str(loadout[1]),
        "utililty": str(loadout[2]),
        "melee": str(loadout[3])
    }


def get_random_stage(rundown_id):
    _rundowns = get_rundown_data()
    stage = _rundowns[rundown_id].get_random_stage()
    difficulty = _rundowns[rundown_id].get_random_difficulty(str(stage))
    return stage, difficulty


def stage_to_json(stage):
    return {
        "stage": str(stage[0]),
        "difficulty": str(stage[1])
    }
