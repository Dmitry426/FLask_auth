from datetime import timedelta
from http import HTTPStatus
from secrets import compare_digest

from flask import Blueprint, request
from flask_jwt_extended import current_user, decode_token, get_jwt, jwt_required
from flask_pydantic import validate

from app.core.alchemy import db
from app.core.redis import redis
from app.models.db_models import Session, User
from app.serializers.auth import ErrorBody, LoginBody, OkBody, RefreshBody, RegisterBody
from app.utils import get_new_tokens

auth = Blueprint("auth", __name__)


@auth.route("/registration", methods=["POST"])
@validate()
def registration(body: RegisterBody):
    """
    Create new user and hash password if login and password valid
    Check if login already exist in DataBase
    Check regex for password
    """

    login_exist = db.session.query(db.exists().where(User.login == body.login)).scalar()
    if login_exist:
        msg = "User with this login already exist, please change login"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT

    new_user = User(login=body.login)
    new_user.set_password(body.password)
    db.session.add(new_user)
    db.session.commit()
    msg = "User successfully created"
    return OkBody(result=msg), HTTPStatus.CREATED


@auth.route("/login", methods=["POST"])
@validate()
def login(body: LoginBody):
    user = User.query.filter_by(login=body.login).one_or_none()
    if not user or not user.check_password(body.password):
        msg = "User with this credentials does not exist"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT
    session = Session(user=user, user_agent=request.user_agent.string)
    db.session.add(session)
    db.session.commit()
    return get_new_tokens(user, request.user_agent.string)


@auth.route("/refresh", methods=["POST"])
@validate()
def refresh(body: RefreshBody):
    claims = decode_token(body.refresh_token)
    user_id = claims["sub"]["user_id"]
    user = User.query.filter_by(id=user_id).one_or_none()
    if not user:
        msg = "Something went wrong"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT

    refresh_key = f"{user.id}_{request.user_agent.string}"
    refresh_token = redis.get(refresh_key)
    if not compare_digest(refresh_token, body.refresh_token):
        msg = "Refresh token not valid"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT

    redis.delete(refresh_key)
    return get_new_tokens(user, request.user_agent.string)


@auth.route("/logout", methods=["POST"])
@validate()
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    redis.set(jti, "", ex=timedelta(hours=1))

    refresh_key = f"{current_user.id}_{request.user_agent.string}"
    redis.delete(refresh_key)

    msg = "User successfully logout"
    return OkBody(result=msg), HTTPStatus.CREATED
