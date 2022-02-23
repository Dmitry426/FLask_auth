from typing import Optional

from flasgger import Swagger
from flask import Flask
from flask.logging import create_logger

from .core.alchemy import init_alchemy

app = Flask(__name__)
swagger = Swagger(app)
logger = create_logger(app)


@app.route("/health")
def root_handler():
    """Check app health
    ---
    tags:
      - utils
    produces:
      - application/json
    schemes: ['http', 'https']
    definitions:
      BoolAnswer:
        type: object
        properties:
          success:
            type: boolean
    responses:
      200:
        schema:
          $ref: '#/definitions/BoolAnswer'
    """
    return {"success": True}


@app.before_first_request
def on_startup():
    """Prepare application and services."""
    init_alchemy(app)


@app.teardown_request
def on_shutdown(error: Optional[BaseException] = None):
    """Teardown application and services."""
    if error is not None:
        logger.exception("%s: %s", type(error).__name__, error)
