from datetime import datetime

from sqlmodel import SQLModel as _SQLModel, Field
from sqlalchemy.orm import declared_attr

from .utils.auth.uuid6 import uuid7, UUID

# id: implements proposal uuid7 draft4


class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__


class BaseIDModel(SQLModel):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(default_factory=datetime.now, nullable=True)


class BaseUUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid7, primary_key=True, index=True, nullable=False
    )
    updated_at: datetime | None = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
    created_at: datetime | None = Field(default_factory=datetime.now)
