from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Params

from ...core.common_deps import get_current_user
from ...core.exceptions.user_exceptions import UserSelfDeleteException
from ...core.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    create_response,
)

from ..schemas.role_schema import IRoleEnum
from ..schemas.user_schema import IUserCreate, IUserRead, IUserUpdate
from ..models.user_model import User
from ..repositories.user_repository import UserRepository, get_user_repository
from ..deps import user_deps as user_deps

router = APIRouter()


@router.get("")
async def get_my_user_data(
    current_user: User = Depends(get_current_user()),
) -> IGetResponseBase[IUserRead]:
    """
    Gets my user profile information
    """
    return create_response(data=current_user)


@router.patch("")
async def update_my_user_data(
    user_obj: IUserUpdate,
    current_user: User = Depends(get_current_user()),
    user_repository: UserRepository = Depends(get_user_repository),
) -> IGetResponseBase[IUserRead]:
    updated_user = await user_repository.update(
        obj_current=current_user, obj_new=user_obj
    )
    return create_response(data=updated_user)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user_directly(
    user_repository: UserRepository = Depends(get_user_repository),
    new_user: IUserCreate = Depends(user_deps.user_exists),
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
) -> IPostResponseBase[IUserRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """
    user = await user_repository.create_with_role(obj_in=new_user)
    return create_response(data=user)


@router.patch("/{user_id}")
async def update_user_by_id_directly(
    user_obj: IUserUpdate,
    user: User = Depends(user_deps.is_valid_user),
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
    user_repository: UserRepository = Depends(get_user_repository),
) -> IGetResponseBase[IUserRead]:
    """
    Updates a user by his/her id

    Required roles:
    - admin
    """

    updated_user = await user_repository.update(
        obj_current=current_user, obj_new=user_obj
    )
    return create_response(data=updated_user)


@router.get("/{user_id}")
async def get_user_by_id(
    user: User = Depends(user_deps.is_valid_user),
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
) -> IGetResponseBase[IUserRead]:
    """
    Gets a user by his/her id

    Required roles:
    - admin
    """
    return create_response(data=user)


@router.delete("/{user_id}")
async def remove_user(
    user_repository: UserRepository = Depends(get_user_repository),
    user_id: UUID = Depends(user_deps.is_valid_user_id),
    current_user: User = Depends(get_current_user(required_roles=[IRoleEnum.admin])),
) -> IDeleteResponseBase[IUserRead]:
    """
    Deletes a user by his/her id

    Required roles:
    - admin
    """
    if current_user.id == user_id:
        raise UserSelfDeleteException()

    user = await user_repository.remove(id=user_id)
    return create_response(data=user, message="User removed")


"""
Below Currently Deprecated
"""


@router.get("/list", deprecated=True)
async def read_users_list(
    user_repository: UserRepository = Depends(get_user_repository),
    params: Params = Depends(),
    current_user: User = Depends(
        get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.founder])
    ),
) -> IGetResponsePaginated[IUserRead]:
    """
    Retrieve users. Requires admin or founder role

    Required roles:
    - admin
    - founder
    """
    users = await user_repository.get_multi_paginated(params=params)
    return create_response(data=users)


@router.get("/order_by_created_at", deprecated=True)
async def get_user_list_order_by_created_at(
    user_repository: UserRepository = Depends(get_user_repository),
    params: Params = Depends(),
    current_user: User = Depends(
        get_current_user(required_roles=[IRoleEnum.admin, IRoleEnum.founder])
    ),
) -> IGetResponsePaginated[IUserRead]:
    """
    Gets a paginated list of users ordered by created datetime

    Required roles:
    - admin
    - founder
    """
    users = await user_repository.get_multi_paginated_ordered(
        params=params, order_by="created_at"
    )
    return create_response(data=users)
