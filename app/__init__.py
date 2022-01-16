from flask import Flask
from flask.logging import create_logger

from .core.alchemy import init_alchemy

app = Flask(__name__)
logger = create_logger(app)


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.before_first_request
def on_startup():
    """Prepare application and services."""
    init_alchemy(app)


@app.teardown_request
def on_shutdown(error=None):
    """Teardown application and services."""
    if error is not None:
        logger.exception("%s: %s", type(error).__name__, error)
