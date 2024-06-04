from typing_extensions import Annotated
from uuid import UUID

from fastapi import Depends, Query, Path


from ...core.exceptions.common_exception import (
    NameNotFoundException,
    IdNotFoundException,
)
from ..models.role_model import Role
from ..repositories.role_repository import RoleRepository, get_role_repository


async def get_user_role_by_name(
    role_name: Annotated[str, Query(title="String compare with name or last name")] = ""
) -> str:
    role = await role.get_role_by_name(name=role_name)
    if not role:
        raise NameNotFoundException(Role, name=role_name)
    return role_name


async def get_user_role_by_id(
    role_id: Annotated[int, Path(title="The id of the role")],
    role_repository: RoleRepository = Depends(get_role_repository),
) -> Role:
    role = await role_repository.get(id=role_id)
    if not role:
        raise IdNotFoundException(Role, id=role_id)
    return role
