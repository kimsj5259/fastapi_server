from enum import Enum
from uuid import UUID

from ...core.decorators.partial import optional

from ..models.role_model import RoleBase


class IRoleCreate(RoleBase):
    pass


# All these fields are optional
@optional
class IRoleUpdate(RoleBase):
    pass


class IRoleRead(RoleBase):
    id: UUID


class IRoleEnum(str, Enum):
    user = "user"
    founder = "founder"
    admin = "admin"
