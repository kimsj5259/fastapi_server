from pydantic import BaseModel
from typing import Optional

from ..models.user_model import ProfileBase

class ISubOpenKeyword(BaseModel):
    is_public: bool
    value: str

class IOpenKeyword(BaseModel):
    sibling_relation: Optional[ISubOpenKeyword] = None
    job: Optional[ISubOpenKeyword] = None
    child: Optional[ISubOpenKeyword] = None
    location: Optional[ISubOpenKeyword] = None

class IProfileCreate(ProfileBase):
    pass


class IProfileUpdate(BaseModel):
    pass

class IFeedImage(BaseModel):
    base_url: str
    detail_path: Optional[list[str]]
    
class IProfile(BaseModel):
    total_diary: int
    total_follower: int
    total_following: int
    nickname: Optional[str]
    email: Optional[str]
    profile_image: Optional[str]
    today_mood_micro_status_id: Optional[int]
    today_interest: Optional[list[str]]
    about_me: Optional[str]
    open_keyword: Optional[IOpenKeyword]
    gender: Optional[str]
    feed_images: Optional[IFeedImage]
    need_verification: Optional[bool]

class IOtherUserPgae(IProfile):
    is_following: Optional[bool]
    
class Follower(BaseModel):
    user_id: int
    nickname: str
    profile_image: str


class IFollower(BaseModel):
    user_id: Optional[int]
    nickname: Optional[str]
    profile_image: Optional[str]
    is_confirmed: Optional[bool] | None = False

class IFollowing(BaseModel):
    following_user_id: Optional[int]
    nickname: Optional[str]
    profile_image: Optional[str]

class IModifyProfile(BaseModel):
    today_mood_micro_status_id: Optional[int]
    nickname: Optional[str]
    about_me: Optional[str]
    open_keyword: Optional[IOpenKeyword]
    profile_image: Optional[str]
    mood_macro_status_id: Optional[int]


class IWithdrawlReason(BaseModel):
    withdrawal_reason: str
