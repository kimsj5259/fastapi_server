from typing import Any
from uuid import UUID
from loguru import logger
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.utils.auth.security import verify_password
from ...core.base_repository import BaseRepository

from ..schemas.profile_schema import IProfileCreate, IProfileUpdate, IModifyProfile
from ..models.user_model import Profile

from ...core.exceptions.common_exception import BadRequestException
from ...core.exceptions.http_error import HttpErrorEnum

class ProfileRepository(BaseRepository[Profile, IProfileCreate, IProfileUpdate]):
    async def get_by_id(
        self, *, user_id: int, db_session: AsyncSession | None = None
    ) -> Profile | None:
        logger.info(f"get_by_id user_id={user_id}")

        db_session = db_session or super().get_db().session
        profile = await db_session.execute(
            select(Profile).where(Profile.user_id == user_id).order_by(Profile.nickname)
        )

        return profile.scalar_one_or_none()

    async def get_by_nickname(
        self, *, nickname: str, db_session: AsyncSession | None = None
    ) -> Profile | None:
        db_session = db_session or super().get_db().session
        users = await db_session.execute(
            select(Profile).where(Profile.nickname == nickname)
        )
        return users.scalar_one_or_none()

    async def save_user_feed(
        self,
        *,
        user_id: int,
        feed_images: list[str],
        db_session: AsyncSession | None = None,
    ) -> None:
        logger.info(f"save_user_feed user_id = {user_id}")

        db_session = db_session or super().get_db().session
        profile_obj = await db_session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )

        try:
            profile = profile_obj.scalar_one()
        except Exception as e:
            raise BadRequestException(HttpErrorEnum.NO_DATA, "profile not found")

        profile.feed_image = feed_images if len(feed_images) != 0 else None
        db_session.add(profile)
        await db_session.commit()

    async def modify_profile(
        self,
        *,
        user_id: int,
        profile: IModifyProfile,                                                              
        db_session: AsyncSession | None = None,
    ) -> None:
        logger.info(f"modify_profile user_id: {user_id} {profile.dict()}")

        db_session = db_session or super().get_db().session
        profile_obj = await db_session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )

        try:
            profile = profile_obj.scalar_one()
        except Exception as e:
            raise BadRequestException(HttpErrorEnum.NO_DATA, "profile not found")

        if profile.profile_image is not None:
            profile.profile_image = profile.profile_image
        if profile.nickname is not None:
            profile.nickname = profile.nickname
        if profile.today_mood_micro_status_id is not None:
            profile.today_mood_micro_status_id = profile.today_mood_micro_status_id
            profile.today_mood_macro_status_id = profile.mood_macro_status_id
        if profile.about_me is not None:
            profile.about_me = profile.about_me
        if profile.open_keyword is not None:
            # pydash를 사용하고 싶으면 간단한데, 설치하면 모듈충돌이 나는듯 함. 일단 이렇게 사용
            open_keyword_dict = profile.open_keyword.dict()
            keys_to_delete = [
                key for key, value in open_keyword_dict.items() if value is None
            ]
            for key in keys_to_delete:
                del open_keyword_dict[key]

            profile.open_keyword = {**profile.open_keyword, **open_keyword_dict} if profile.open_keyword is not None else open_keyword_dict

        db_session.add(profile)
        await db_session.commit()


def get_profile_repository() -> ProfileRepository:
    return ProfileRepository(Profile)
