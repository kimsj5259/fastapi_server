from typing import List

from sqlmodel import Field, Relationship

from ...core.base_model import BaseIDModel
from .journal_model import Journal


class MoodMacroStatus(BaseIDModel, table=True):
    __tablename__ = "mood_macro_status"

    mood_macro: str
    mood_micro: List["MoodMicroStatus"] = Relationship(back_populates="mood_macro")
    journal: "Journal" = Relationship(back_populates="mood_macro")


class MoodMicroStatus(BaseIDModel, table=True):
    __tablename__ = "mood_micro_status"

    mood_micro: str
    mood_macro_status_id: int = Field(
        foreign_key="mood_macro_status.id", nullable=False
    )
    mood_macro: MoodMacroStatus = Relationship(back_populates="mood_micro")
    journal: "Journal" = Relationship(back_populates="mood_micro")