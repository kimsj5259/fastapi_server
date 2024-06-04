from datetime import datetime
from pydantic import BaseModel

from ..models.user_model import ProfileBase
from .user_schema import IUserRead


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    user: IUserRead


class ExternalCallbackResponse(Token):
    profile: ProfileBase


class TokenRead(BaseModel):
    access_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class OAuthTokenBase(BaseModel):
    access_token: str
    token_type: str
    id_token: str
    expires_in: int


class OAuthToken(OAuthTokenBase):
    refresh_token: str
    scope: str | None = None
    refresh_token_expires_in: int | None = None


class KakaoOAuthProfileInfo(BaseModel):
    nickname: str
    thumbnail_image_url: str | None = None
    profile_image_url: str | None = None


class KakaoOAuthAccountInfo(BaseModel):
    profile: KakaoOAuthProfileInfo
    email: str
    # age_range: str
    # birthday: str
    # birthday_type: str
    # gender: str


class KakaoOAuthUserInfo(BaseModel):
    id: str
    connected_at: datetime
    kakao_account: KakaoOAuthAccountInfo


class ExternalProviderCallbackResponse(BaseModel):
    token: OAuthToken
    user: IUserRead
