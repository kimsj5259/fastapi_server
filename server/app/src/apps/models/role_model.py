from sqlmodel import SQLModel, Relationship, Field

from ...core.base_model import BaseIDModel, BaseUUIDModel


class RoleBase(SQLModel):
    name: str = Field(nullable=False)
    description: str = Field(nullable=True)


class Role(BaseIDModel, RoleBase, table=True):
    __tablename__ = "role"

    user: list["User"] = Relationship(  # noqa: F821
        back_populates="role", sa_relationship_kwargs={"lazy": "selectin"}
    )
