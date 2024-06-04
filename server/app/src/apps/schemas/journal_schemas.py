from datetime import date, datetime
from pydantic import BaseModel

from ..models.journal_model import JournalBase, Journal
from ...core.decorators.partial import optional
from ..models.journal_model import WithWhomEnum, TopicEnum


class JournalSpecifiedDateReadData(BaseModel):
    journal_id: int
    context: str
    mood_macro_status_id: int
    mood_micro_status_id: int


@optional
class IJournalRead(Journal):
    pass


class IJournalSpecifiedDateRead(BaseModel):
    journal_time_at: date
    data: list[JournalSpecifiedDateReadData]


@optional
class IJournalCreate(BaseModel):
    id: int
    user_id: int
    with_whom: WithWhomEnum
    topic: list[TopicEnum]
    reason: str
    action_from_emotion: str
    context: str
    journal_time_at: date
    mood_macro_status_id: int
    mood_micro_status_id: int
    images: object
    created_at: datetime
    updated_at: datetime


@optional
class IJournalUpdate(JournalBase):
    pass


class ListByMonthResponse(BaseModel):
    journal_time_at: str
    mood_micro_status_id: int
    mood_macro_status_id: int
