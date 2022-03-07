from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .roles import RoleBody


class UserBody(BaseModel):
    id: UUID
    login: str
    roles: List[RoleBody]


class PaginationUsersBody(BaseModel):
    count: int
    total_pages: int
    page: int
    results: List[UserBody]


class QueryPaginationBode(BaseModel):
    search: Optional[str]
    page: int = 1
    per_page: int = 20
