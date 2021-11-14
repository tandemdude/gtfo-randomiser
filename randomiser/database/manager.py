import contextlib
import datetime
import os
from importlib import resources

import psycopg2
from flask import g

from randomiser.database import sql


@contextlib.contextmanager
def get_cursor(conn, commit: bool = False):
    """
    Context manager to automatically manage database connections. Acquires a connection for
    use within the context manager and gives a cursor to execute queries through. Closes the cursor
    and puts the connection back into the pool once the context manager has been exited.
    Args:
        conn (:obj:`psycopg2.connection`): Connection object to acquire cursor for.
        commit (:obj:`bool`): Whether or not to commit changes to the database once the context is exited.
            Defaults to ``False``.
    """
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        if commit:
            conn.commit()


class DatabaseManager:
    def __init__(self):
        self._connector = self._create_database_connection()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def _create_database_connection(self):
        return psycopg2.connect(os.environ["DATABASE_URL"])

    def close_connection(self):
        return self._connector.close()

    def create_schema(self):
        schema = resources.read_text(sql, "schema.sql")
        with get_cursor(self._connector, commit=True) as cur:
            cur.execute(schema)

    def delete_tokens_for_same_user(self, user_id):
        with get_cursor(self._connector, commit=True) as cur:
            cur.execute("DELETE FROM credentials WHERE user_id = %s;", (user_id,))

    def save_tokens(self, user_id, username, discrim, tokens):
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=tokens["expires_in"]
        )
        with get_cursor(self._connector, commit=True) as cur:
            cur.execute(
                "INSERT INTO credentials(user_id, username, discrim, access_token, refresh_token, expires_at) VALUES(%s, %s, %s, %s, %s, %s);",
                (
                    user_id,
                    username,
                    discrim,
                    tokens["access_token"],
                    tokens["refresh_token"],
                    expires_at,
                ),
            )

    def create_daily_submission(self, user_id, time, url):
        date = datetime.datetime.now(datetime.timezone.utc).date().strftime("%Y-%m-%d")
        with get_cursor(self._connector, commit=True) as cur:
            cur.execute(
                "INSERT INTO daily_runs(run_date, run_time, evidence_url, user_id) VALUES(%s, %s, %s, %s) RETURNING run_id;",
                (date, time, url, user_id),
            )
            out = cur.fetchone()
        return out[0] if isinstance(out, tuple) else out

    def get_top_ten_daily_runs(self, date):
        with get_cursor(self._connector) as cur:
            cur.execute(
                """
                SELECT
                    credentials.username || '#' || credentials.discrim,
                    daily_runs.run_time, daily_runs.evidence_url,
                    daily_runs.run_verified,
                    daily_runs.run_id
                FROM daily_runs
                INNER JOIN 
                    credentials 
                        ON credentials.user_id = daily_runs.user_id
                WHERE daily_runs.run_date = %s
                ORDER BY daily_runs.run_time
                LIMIT 10;
                """,
                (date,),
            )
            rows = cur.fetchall()
        return rows

    def save_daily_run(self, date, p1, p2, p3, p4, stage):
        with get_cursor(self._connector, commit=True) as cur:
            cur.execute(
                "INSERT INTO daily_challenges(loadout_date, p1, p2, p3, p4, stage) VALUES(%s, %s, %s, %s, %s, %s);",
                (date, p1, p2, p3, p4, stage),
            )

    def get_daily(self, date):
        with get_cursor(self._connector) as cur:
            cur.execute(
                "SELECT p1, p2, p3, p4, stage FROM daily_challenges WHERE loadout_date = %s;",
                (date,),
            )
            out = cur.fetchone()
        return out or None

    def verify_run(self, run_id):
        with get_cursor(self._connector, commit=True) as cur:
            cur.execute(
                "UPDATE daily_runs SET run_verified = %s WHERE run_id = %s;",
                (True, run_id),
            )

    def delete_run(self, run_id):
        with get_cursor(self._connector, commit=True) as cur:
            cur.execute("DELETE FROM daily_runs WHERE run_id = %s;", (run_id,))

    def get_username_and_discrim(self, user_id):
        with get_cursor(self._connector) as cur:
            cur.execute(
                "SELECT username, discrim FROM credentials WHERE user_id = %s;",
                (user_id,),
            )
            data = cur.fetchone()
        return "#".join(data)

    def get_daily_runs_for_user(self, user_id):
        with get_cursor(self._connector) as cur:
            cur.execute(
                "SELECT run_date, run_time, evidence_url, run_verified, run_id FROM daily_runs WHERE user_id = %s ORDER BY run_date DESC, run_time;",
                (user_id,),
            )
            data = cur.fetchall()
        return data

    def save_state(self, state):
        with get_cursor(self._connector, commit=True) as cur:
            cur.execute("INSERT INTO states(state) VALUES(%s);", (state,))

    def validate_state(self, state):
        with get_cursor(self._connector) as cur:
            cur.execute("SELECT state FROM states WHERE state = %s;", (state,))
            data = cur.fetchone()
        return data[0] if data else None if isinstance(data, tuple) else data

    def delete_state(self, state):
        with get_cursor(self._connector, commit=True) as cur:
            cur.execute("DELETE FROM states WHERE state = %s;", (state,))


def get_database_manager():
    if "dbm" not in g:
        g.dbm = DatabaseManager()
    return g.dbm
