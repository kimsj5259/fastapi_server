from typing import List, Optional
from enum import Enum
from datetime import datetime, date
from sqlmodel import SQLModel, Column, Text, Field, Relationship, ARRAY, String
from ...core.base_model import BaseIDModel


class WithWhomEnum(str, Enum):
    family = "family"
    friend = "friend"
    other_half = "other_half"
    acquaintance = "acquaintance"
    alone = "alone"
    pet = "pet"


class TopicEnum(str, Enum):
    mental_health = "mental_health"
    marriage_parenting = "marriage_parenting"
    money_business = "money_business"
    personal_relationship = "personal_relationship"
    parting_divorce = "parting_divorce"
    job_career = "job_career"
    family = "family"
    date_look = "date_look"
    illness = "illness"
    etc = "etc"


class JournalBase(SQLModel):
    with_whom: WithWhomEnum = Field(nullable=False)
    topic: Optional[List[TopicEnum]] = Field(sa_column=Column(ARRAY(String)), nullable=False)
    reason: str = Field(sa_column=Column(Text), nullable=False)
    action_from_emotion: str = Field(sa_column=Column(Text))
    context: str = Field(sa_column=Column(Text), nullable=False)
    journal_time_at: date = Field(
        default=None, nullable=False
    )  # 유저가 과거의 기억을 적을수도 있을 경우를 위한 컬럼
    mood_macro_status_id: Optional[int] = Field(
        default=None, foreign_key="mood_macro_status.id", nullable=False
    )
    mood_micro_status_id: Optional[int] = Field(
        default=None, foreign_key="mood_micro_status.id", nullable=False
    )


class Journal(BaseIDModel, JournalBase, table=True):
    __tablename__ = "journal"

    images: Optional[List[str]] = Field(sa_column=Column(ARRAY(String)), nullable=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    updated_at: datetime | None = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship(back_populates="journal")
    mood_macro: Optional["MoodMacroStatus"] = Relationship(back_populates="journal")
    mood_micro: Optional["MoodMicroStatus"] = Relationship(back_populates="journal")
    