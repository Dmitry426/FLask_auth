from datetime import timedelta

from flask_jwt_extended import create_access_token, create_refresh_token

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
    refresh_key = str(user.id) + "_" + user_agent

    # Put refresh token in redis for validate refreshing
    redis.set(refresh_key, refresh_token, ex=timedelta(days=JWTSettings().refresh_exp))
    return TokenBody(access_token=access_token, refresh_token=refresh_token)
