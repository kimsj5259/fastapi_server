from enum import Enum

from ...core.decorators.partial import optional

from ..models.user_model import UserBase
from .role_schema import IRoleRead


class IUserCreate(UserBase):
    # password: str | None

    # class Config:
    #     hashed_password = None
    pass


# All these fields are optional
@optional
class IUserUpdate(UserBase):
    pass


class IUserRead(UserBase):
    role: IRoleRead | None = None


class IUserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
