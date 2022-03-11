from http import HTTPStatus

from flask import Blueprint, request
from flask_pydantic import validate
from sqlalchemy import func

from app.core.alchemy import db
from app.models.db_models import Role, User
from app.serializers.auth import ErrorBody
from app.serializers.roles import RoleBody
from app.serializers.users import PaginationUsersBody, QueryPaginationBody, UserBody
from app.utils import permissions_required

users = Blueprint("users", __name__)


@users.route("/", methods=["GET"])
@validate()
@permissions_required("admin")
def roles_list(query: QueryPaginationBody):
    if query.search:
        queryset = User.query.filter(
            func.lower(User.login).startswith(query.search.lower())
        ).order_by(User.login)
    else:
        queryset = User.query.order_by(User.login)

    pagination = queryset.paginate(
        page=query.page, per_page=query.per_page, error_out=False
    )

    results = [
        UserBody(
            id=user.id,
            login=user.login,
            roles=[RoleBody(id=role.id, name=role.name) for role in user.roles],
        )
        for user in pagination.items
    ]

    return PaginationUsersBody(
        count=pagination.total,
        total_pages=pagination.pages,
        page=pagination.page,
        results=results,
    )


@users.route("/<user_id>/roles/<role_id>", methods=["PUT", "DELETE"])
@validate()
@permissions_required("admin")
def set_role(user_id: str, role_id: int):
    user = User.query.get(user_id)
    role = Role.query.get(role_id)
    if not user or not role:
        msg = "User or Role not found"
        return ErrorBody(error=msg), HTTPStatus.NOT_FOUND

    if request.method == "PUT":
        user.roles.append(role)

    elif request.method == "DELETE":
        try:
            user.roles.remove(role)
        except ValueError:
            msg = "User does not have this role"
            return ErrorBody(error=msg), HTTPStatus.CONFLICT

    db.session.commit()
    return UserBody(
        id=user.id,
        login=user.login,
        roles=[RoleBody(id=role.id, name=role.name) for role in user.roles],
    )