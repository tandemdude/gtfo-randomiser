import logging

import flask

from randomiser import api, endpoints
from randomiser.database import manager

_LOGGER = logging.getLogger("randomiser")
logging.basicConfig(level=logging.INFO)


def create_app() -> flask.Flask:
    _LOGGER.info("Creating application")
    app = flask.Flask(__name__)

    @app.teardown_appcontext
    def close_dbm(_):
        dbm = flask.g.pop("dbm", None)
        if dbm is not None:
            dbm.close_connection()

    with manager.DatabaseManager() as dbm:
        dbm.create_schema()

    endpoints.setup(app)
    api.setup(app)
    return app
