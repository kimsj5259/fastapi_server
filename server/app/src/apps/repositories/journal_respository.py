from datetime import date
from uuid import UUID

from sqlmodel import select, text, func
from sqlmodel.ext.asyncio.session import AsyncSession
from ...core.base_repository import BaseRepository
from ..models.journal_model import Journal
from ..schemas.journal_schemas import IJournalCreate, IJournalUpdate


class JournalRepository(BaseRepository[Journal, IJournalCreate, IJournalUpdate]):
    async def get_by_specified_date(
        self,
        *,
        user_id: int,
        start_date: date,
        end_date: date,
        db_session: AsyncSession | None = None,
    ) -> Journal | None:
        db_session = db_session or super().get_db().session
        query = select(
            self.model.journal_time_at,
            func.json_agg(
                func.json_build_object(
                    "journal_id", self.model.id,
                    "context", self.model.context, # 뭐뭐 줄자 추후 변경 가능성 있음
                    "mood_macro_status_id", self.model.mood_macro_status_id,
                    "mood_micro_status_id", self.model.mood_micro_status_id
                )
            ).label("data")
        ).where(
            self.model.journal_time_at.between(start_date, end_date)
            & (self.model.user_id == user_id)
        ).group_by(func.DATE(self.model.journal_time_at))
        response = await db_session.execute(query)

        return response.all()

    def get_by_month_query(self, *, user_id: int, date: date):
        client_date = date.strftime("%Y-%m")
        query = select(Journal).where(
            (text("TO_CHAR(created_at, 'YYYY-MM') LIKE :year_month")).params(
                year_month=f"{client_date}%"
            )
            & (Journal.user_id == user_id)
        )
        return query
    
    def get_by_month_query_with_journal_time_at(self, *, user_id: int, date: date):
        client_date = date.strftime("%Y-%m")
        query = select(Journal).where(
            (text("TO_CHAR(journal_time_at, 'YYYY-MM') LIKE :year_month")).params(
                year_month=f"{client_date}%"
            )
            & (Journal.user_id == user_id)
        )
        return query

    async def get_by_month(
        self, *, user_id: int, date: date, db_session: AsyncSession | None = None
    ) -> list[Journal]:
        db_session = db_session or super().get_db().session
        query = self.get_by_month_query_with_journal_time_at(user_id=user_id, date=date)
        response = await db_session.execute(query)
        return response.scalars().all()

    async def remove(
        self, *, id: UUID | str, db_session: AsyncSession | None = None
    ) -> Journal:
        db_session = db_session or super().get_db().session
        response = await db_session.execute(
            select(self.model).where(self.model.id == id)
        )
        obj = response.scalar_one()

        await db_session.delete(obj)
        await db_session.commit()
        return obj

    async def count_total_journal(
        self, *, user_id: int, db_session: AsyncSession | None = None
    ) -> int:
        db_session = db_session or super().get_db().session
        
        count_query = select(func.count()).select_from(Journal).where(Journal.user_id == user_id)
        count_result = await db_session.execute(count_query)
        
        return count_result.scalar()

def get_journal_repository() -> JournalRepository:
    return JournalRepository(Journal)