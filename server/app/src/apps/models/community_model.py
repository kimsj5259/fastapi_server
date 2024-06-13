from typing import Optional, List
from sqlalchemy import UniqueConstraint

from sqlmodel import SQLModel, Field, Relationship, Column, ARRAY, Integer, JSON

from ...core.base_model import BaseIDModel


class Subject(SQLModel, table=True):
    __tablename__ = "subject"

    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)


class SubjectSub(SQLModel, table=True):
    __tablename__ = "subject_sub"

    id: int = Field(primary_key=True)
    parent_subject_id: int = Field(foreign_key="subject.id", nullable=False)

    name: str = Field(nullable=False)
    eng_name: str = Field(nullable=False)

    parent_subject: "Subject" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "SubjectSub.parent_subject_id==Subject.id",
            # "lazy": "joined",
        }
    )


"""
Only Get from subject_suggestion & user_suggestion only, Create depends on ML
"""


class SubjectSuggestion(BaseIDModel, table=True):
    __tablename__ = "subject_suggestion"

    user_id: int = Field(foreign_key="user.id", unique=True)
    recommended_subject_ids: Optional[dict] = Field(
        sa_column=Column(JSON), nullable=False
    )

    subject_suggestion_user: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "SubjectSuggestion.user_id==User.id",
            # "lazy": "joined",
        }
    )


class UserSuggestion(BaseIDModel, table=True):
    __tablename__ = "user_suggestion"
    __table_args__ = (
        UniqueConstraint("user_id", "subject_id", name="user_subject_unique"),
    )

    user_id: int = Field(foreign_key="user.id")
    subject_id: int = Field(foreign_key="subject.id")
    recommended_user_ids: Optional[List[int]] = Field(
        sa_column=Column(ARRAY(Integer)), nullable=False
    )

    user_suggestion_user: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "UserSuggestion.user_id==User.id",
            # "lazy": "joined",
        }
    )
    user_suggestion_subject: "Subject" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "UserSuggestion.subject_id==Subject.id",
            # "lazy": "joined",
        }
    )
