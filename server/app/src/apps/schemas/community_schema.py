from pydantic import BaseModel
from typing import Optional

from ...core.decorators.partial import optional
from ..models.community_model import SubjectSuggestion, UserSuggestion


class ISubjectSuggestionCreate(BaseModel):
    pass

class ISubjectSuggestionUpdate(BaseModel):
    pass


@optional
class ISubjectSuggestionRead(SubjectSuggestion):
    pass


class IUserSuggestionCreate(BaseModel):
    pass

class IUserSuggestionUpdate(BaseModel):
    pass


@optional
class IUserSuggestionRead(UserSuggestion):
    pass


@optional
class MatchedUserResponse(BaseModel):
    user_id:Optional[int]
    nickname:Optional[str]
    profile_image:Optional[str]
    top_values: Optional[list]


class IMatchedUserResponse(BaseModel):
    data: list[MatchedUserResponse]
    base_url: str
