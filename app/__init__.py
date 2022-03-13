import http
from datetime import timedelta
from http import HTTPStatus
from typing import Optional

from flasgger import Swagger
from flask import Flask
from flask.json import jsonify
from flask.logging import create_logger
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import IntegrityError

from .api.auth import auth
from .api.roles import roles
from .api.users import users
from .core.alchemy import db, init_alchemy
from .core.config import AppSettings, JWTSettings
from .core.redis import redis
from .models.db_models import User
from .serializers.auth import ErrorBody
from .utils import create_superuser

app = Flask(__name__)
swagger = Swagger(app)
logger = create_logger(app)

# Setup the Flask-JWT-Extended extension
jwt_conf = JWTSettings()
app.config["JWT_SECRET_KEY"] = jwt_conf.secret
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=jwt_conf.access_exp)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=jwt_conf.refresh_exp)
app.config["JWT_ERROR_MESSAGE_KEY"] = "error"
jwt = JWTManager(app)

# Setup routing
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(roles, url_prefix="/roles")
app.register_blueprint(users, url_prefix="/users")


# noinspection PyUnusedLocal
@app.errorhandler(403)
def permission_denied(exc: BaseException):
    return jsonify({"error": "You don't have permissions"}), http.HTTPStatus.FORBIDDEN


# noinspection PyUnusedLocal
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = redis.get(jti)
    return token_in_redis is not None


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]["user_id"]
    user = User.query.filter_by(id=identity).one_or_none()
    if not user:
        msg = "Something went wrong"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT
    return user


@app.route("/health")
def health_handler():
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
    db.create_all()

    app_settings = AppSettings()
    if app_settings.superuser_enable:
        try:
            create_superuser()
        except IntegrityError:
            pass


@app.teardown_request
def on_shutdown(error: Optional[BaseException] = None):
    """Teardown application and services."""
    if error is not None:
        logger.exception("%s: %s", type(error).__name__, error)
