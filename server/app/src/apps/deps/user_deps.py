from typing_extensions import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status

from ...core.exceptions.common_exception import IdNotFoundException

from ..schemas.user_schema import IUserCreate, IUserRead
from ..models.role_model import Role
from ..models.user_model import User
from ..repositories.role_repository import RoleRepository, get_role_repository
from ..repositories.user_repository import UserRepository, get_user_repository


async def user_exists(
    new_user: IUserCreate,
    user_repository: UserRepository = Depends(get_user_repository),
    role_repository: RoleRepository = Depends(get_role_repository),
) -> IUserCreate:
    user = await user_repository.get_by_email(email=new_user.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same email",
        )
    role = await role_repository.get(id=new_user.role_id)
    if not role:
        raise IdNotFoundException(Role, id=new_user.role_id)

    return new_user


async def is_valid_user(
    user_id: Annotated[UUID, Path(title="The UUID id of the user")],
    user_repository: UserRepository = Depends(get_user_repository),
) -> IUserRead:
    user = await user_repository.get(id=user_id)
    if not user:
        raise IdNotFoundException(User, id=user_id)

    return user


async def is_valid_user_id(
    user_id: Annotated[UUID, Path(title="The UUID id of the user")],
    user_repository: UserRepository = Depends(get_user_repository),
) -> IUserRead:
    user = await user_repository.get(id=user_id)
    if not user:
        raise IdNotFoundException(User, id=user_id)

    return user_id
