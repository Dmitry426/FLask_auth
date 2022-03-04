from datetime import timedelta
from http import HTTPStatus

from flask import Blueprint, request
from flask_jwt_extended import (
    current_user,
    decode_token,
    get_current_user,
    get_jwt,
    jwt_required,
)
from flask_pydantic import validate

from app.core.alchemy import db
from app.core.redis import redis
from app.models.db_models import Session, User
from app.serializers.auth import (
    ErrorBody,
    HistoryBody,
    LoginBody,
    OkBody,
    RefreshBody,
    RegisterBody,
)
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


@auth.route("/change", methods=["POST"])
@validate()
@jwt_required()
def change_password(body: RegisterBody):
    user_uuid = get_current_user().id
    user = User.query.filter_by(id=user_uuid).one_or_none()
    new_login_exist = db.session.query(
        db.exists().where(User.login == body.login)
    ).scalar()

    if new_login_exist:
        msg = "User with this login already exist, please change login"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT

    if user.check_password(body.password):
        msg = "This password matches with the current one, Please enter new one "
        return ErrorBody(error=msg), HTTPStatus.CONFLICT

    user.login = body.login
    user.set_password(body.password)
    db.session.commit()
    msg = "Password and Login successfully changed"
    return OkBody(result=msg), HTTPStatus.ACCEPTED


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


@auth.route("/history", methods=["GET"])
@validate(response_many=True)
@jwt_required()
def auth_history():
    user_uuid = get_current_user().id
    history = Session.query.filter_by(user_id=user_uuid).all()
    return [
        HistoryBody(user_agent=row.user_agent, auth_date=row.auth_date)
        for row in history
    ]


@auth.route("/refresh", methods=["POST"])
@validate()
def refresh(body: RefreshBody):
    claims = decode_token(body.refresh_token)
    user_id = claims["sub"]["user_id"]
    user = User.query.filter_by(id=user_id).one_or_none()
    if not user:
        msg = "Something went wrong"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT

    refresh_key = str(user.id) + "_" + request.user_agent.string
    if redis.get(refresh_key) != body.refresh_token:
        msg = "Refresh token not valid"
        return ErrorBody(error=msg), HTTPStatus.CONFLICT

    redis.delete(refresh_key)
    return get_new_tokens(user, request.user_agent.string)


@auth.route("/logout", methods=["GET"])
@validate()
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    redis.set(jti, "", ex=timedelta(hours=1))

    refresh_key = str(current_user.id) + "_" + request.user_agent.string
    redis.delete(refresh_key)

    msg = "User successfully logout"
    return OkBody(result=msg), HTTPStatus.CREATED
