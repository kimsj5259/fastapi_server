from typing import Optional, List
from datetime import datetime, date

from pydantic import EmailStr
from sqlmodel import (
    Field,
    SQLModel,
    Relationship,
    Column,
    ARRAY,
    String,
    Text,
    JSON,
    UniqueConstraint
)

from ...core.base_model import BaseIDModel
from .journal_model import Journal
from ...core.schemas.common_schema import GenderEnum
from .role_model import Role

"""
User
"""


class UserBase(SQLModel):
    user_name: str = Field(nullable=False)
    oauth_provider: str = Field(nullable=False)
    provider_user_id: str = Field(nullable=True)
    email: EmailStr = Field(
        nullable=True, index=True, sa_column_kwargs={"unique": True}
    )
    gender: GenderEnum | None = Field(default=GenderEnum.other, nullable=True)
    birth_date: date | None = Field(nullable=True)
    is_active: bool = Field(default=True)
    role_id: Optional[int] = Field(default=None, foreign_key="role.id", unique=True)

    withdrawal_reason: str | None = Field(nullable=True)
    withdrawn_at: datetime | None = Field(nullable=True)
    updated_at: datetime | None = Field(default_factory=datetime.now)

    terms_of_use_agreement: bool = Field(default=False)
    use_of_information_agreement: bool = Field(default=False)


class User(BaseIDModel, UserBase, table=True):
    __tablename__ = "user"

    # hashed_password : str | None = Field(nullable=False, index=True)
    role: Optional["Role"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "joined"}
    )
    journal: List["Journal"] = Relationship(back_populates="user")


"""
Profile
"""


class ProfileBase(SQLModel):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", unique=True)
    nickname: str | None = Field(nullable=True, unique=True)
    profile_image: str | None = Field(nullable=True)
    about_me: str | None = Field(sa_column=Column(Text))
    today_interest: list[str] | None = Field(sa_column=Column(ARRAY(String)))
    open_keyword: dict | None = Field(sa_column=Column(JSON), nullable=True)
    updated_at: datetime | None = Field(default_factory=datetime.now)
    today_mood_macro_status_id: int | None = Field(
        default=None, foreign_key="mood_macro_status.id"
    )
    today_mood_micro_status_id: int | None = Field(
        default=None, foreign_key="mood_micro_status.id"
    )
    feed_image: List[str] | None = Field(sa_column=Column(ARRAY(String)))


class Profile(BaseIDModel, ProfileBase, table=True):
    __tablename__ = "profile"

    user: Optional[User] = Relationship(back_populates="profile")
    mood_macro: "MoodMacroStatus" = Relationship(back_populates="profile")
    mood_micro: "MoodMicroStatus" = Relationship(back_populates="profile")



"""
Friend
"""


class Friend(BaseIDModel, table=True):
    __tablename__ = "friend"

    __table_args__ = (
        UniqueConstraint("user_id", "following_user_id", name="user_id_following_user_id_unique"),
    )
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    following_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    is_confirmed: Optional[bool] = Field(default=False)
    updated_at: datetime | None = Field(default_factory=datetime.now, nullable=True)

    friend_user: Optional[User] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Friend.user_id==User.id",
            "lazy": "joined",
        }
    )
    follwing: Optional[User] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Friend.following_user_id==User.id",
            "lazy": "joined",
        }
    )
