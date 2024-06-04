from enum import Enum

from pydantic import BaseModel

from ...apps.schemas.role_schema import IRoleRead


class IMetaGeneral(BaseModel):
    roles: list[IRoleRead]


class IOrderEnum(str, Enum):
    ascendent = "ascendent"
    descendent = "descendent"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class GenderEnum(str, Enum):
    female = "female"
    male = "male"
    other = "other"


class OauthProvider(str, Enum):
    kakao = "kakao"
    apple = "apple"
    