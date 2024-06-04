from loguru import logger
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from ...core.base_repository import BaseRepository
from ..models.mood_model import MoodMicroStatus
from ..schemas.mood_schemas import IMoodMicroCreate, IMoodMicroUpdate

from ...core.exceptions.common_exception import BadRequestException
from ...core.exceptions.http_error import HttpErrorEnum

class MoodMicroStatusRepository(
    BaseRepository[MoodMicroStatus, IMoodMicroCreate, IMoodMicroUpdate]
):
    async def find_mood_macro_id_with_micro_id(
        self, *, db_session: AsyncSession | None = None
    ) -> MoodMicroStatus | None:
        db_session = db_session or super().get_db().session
        query = select(MoodMicroStatus)

        # response = await db_session.execute(query)

        return query

    async def get_mood_micro_status_by_id(
        self, *, id: int, db_session: AsyncSession | None = None
    ) -> MoodMicroStatus | None:
        logger.info(f"get_mood_micro_status_by_id id: {id}")
        
        db_session = db_session or super().get_db().session
        mood_obj = await db_session.execute(select(MoodMicroStatus).where(MoodMicroStatus.id == id))
        
        try:
            mood = mood_obj.scalar_one()
        except Exception as e:
            raise BadRequestException(HttpErrorEnum.NO_DATA, "Mood not found")

        return mood


def get_mood_micro_repository() -> MoodMicroStatusRepository:
    return MoodMicroStatusRepository(MoodMicroStatus)
