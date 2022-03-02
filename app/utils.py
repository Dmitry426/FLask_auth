from datetime import timedelta
from functools import wraps

from flask import abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    verify_jwt_in_request,
)

from app.core.config import JWTSettings
from app.core.redis import redis
from app.models.db_models import User
from app.serializers.auth import TokenBody


def get_new_tokens(user: User, user_agent: str) -> TokenBody:
    """
    Create new access and refresh tokens with user id and roles
    """
    identity = {"user_id": user.id, "roles": [role.name for role in user.roles]}
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    refresh_key = f"{user.id}_{user_agent}"

    # Put refresh token in redis for validate refreshing
    redis.set(refresh_key, refresh_token, ex=timedelta(days=JWTSettings().refresh_exp))
    return TokenBody(access_token=access_token, refresh_token=refresh_token)


def permissions_required(role: str):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = current_user
            user_roles = get_jwt()["sub"]["roles"]
            if user.is_superuser or role in user_roles:
                return fn(*args, **kwargs)
            return abort(403)

        return decorator

    return wrapper
