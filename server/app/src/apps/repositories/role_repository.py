from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from ...core.base_repository import BaseRepository

from ..schemas.role_schema import IRoleCreate, IRoleUpdate
from ..models.role_model import Role
from ..models.user_model import User


class RoleRepository(BaseRepository[Role, IRoleCreate, IRoleUpdate]):
    async def get_role_by_name(
        self, *, name: str, db_session: AsyncSession | None = None
    ) -> Role:
        db_session = db_session or super().get_db().session
        role = await db_session.execute(select(Role).where(Role.name == name))
        return role.scalar_one_or_none()

    async def add_role_to_user(self, *, user: User, role_id: int) -> Role:
        db_session = super().get_db().session
        role = await super().get(id=role_id)
        role.user.append(user)
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)
        return role


def get_role_repository() -> RoleRepository:
    return RoleRepository(Role)
