import datetime
from typing import Any
from uuid import UUID
from loguru import logger
import random
import string

from pydantic.networks import EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.utils.auth.security import verify_password
from ...core.base_repository import BaseRepository
from ...core.constants.constant import WITHDRAWL_POSTFIX

from ..schemas.user_schema import IUserCreate, IUserUpdate
from ..models.user_model import User, Profile


class UserRepository(BaseRepository[User, IUserCreate, IUserUpdate]):
    async def get_by_email(
        self, *, email: str, db_session: AsyncSession | None = None
    ) -> User | None:
        db_session = db_session or super().get_db().session
        users = await db_session.execute(select(User).where(User.email == email))
        return users.scalar_one_or_none()

    async def get_by_user_name(
        self, *, user_name: str, db_session: AsyncSession | None = None
    ) -> User | None:
        db_session = db_session or super().get_db().session
        users = await db_session.execute(
            select(User).where(User.user_name == user_name)
        )
        return users.scalar_one_or_none()

    async def get_by_provider_user_id(
        self, *, provider_user_id: str, db_session: AsyncSession | None = None
    ) -> User | None:
        db_session = db_session or super().get_db().session
        users = await db_session.execute(
            select(User)
            .where(User.provider_user_id == provider_user_id)
            .where(User.is_active == True)
        )
        return users.scalar_one_or_none()

    async def get_by_id_active(self, *, id: UUID) -> User | None:
        user = await super().get(id=id)
        if not user:
            return None
        if user.is_active is False:
            return None

        return user

    async def create_with_role(
        self, *, obj_in: IUserCreate, db_session: AsyncSession | None = None
    ) -> User:
        db_session = db_session or super().get_db().session
        db_obj = User.from_orm(obj_in)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def update_is_active(
        self, *, db_obj: list[User], obj_in: int | str | dict[str, Any]
    ) -> User | None:
        response = None
        db_session = super().get_db().session
        for x in db_obj:
            x.is_active = obj_in.is_active
            db_session.add(x)
            await db_session.commit()
            await db_session.refresh(x)
            response.append(x)
        return response

    async def authenticate(self, *, email: EmailStr, password: str) -> User | None:
        user = await self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def remove(
        self, *, id: UUID | str, db_session: AsyncSession | None = None
    ) -> User:
        db_session = db_session or super().get_db().session
        response = await db_session.execute(
            select(self.model).where(self.model.id == id)
        )
        obj = response.scalar_one()

        await db_session.delete(obj)
        await db_session.commit()
        return obj

    async def withdraw_user(
        self,
        *,
        user_id: int,
        withdrawal_reason: str,
        db_session: AsyncSession | None = None,
    ) -> None:
        logger.info(f"withdraw_user user_id: {user_id}")
        db_session = db_session or super().get_db().session
        response = await db_session.execute(select(User).where(User.id == user_id))
        user = response.scalar_one()

        user.is_active = False
        user.withdrawn_at = datetime.datetime.now()
        user.withdrawal_reason = withdrawal_reason
        
        # 랜덤 문자열을 생성
        random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(WITHDRAWL_POSTFIX))
        user.email = f'{user.email}_{random_string}'
        
        db_session.add(user)
        
        response = await db_session.execute(select(Profile).where(Profile.user_id == user_id))
        profile = response.scalar_one()
        
        profile.nickname = f'{profile.nickname}_{random_string}'
        
        db_session.add(profile)
        
        await db_session.commit()


def get_user_repository() -> UserRepository:
    return UserRepository(User)
