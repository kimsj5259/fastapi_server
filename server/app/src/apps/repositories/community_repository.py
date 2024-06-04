from sqlmodel import select, text
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.base_repository import BaseRepository

from ..models.community_model import UserSuggestion, SubjectSuggestion
from ..schemas.community_schema import ISubjectSuggestionCreate, ISubjectSuggestionUpdate


class CommunityRepository(BaseRepository[UserSuggestion, ISubjectSuggestionCreate, ISubjectSuggestionUpdate]):
    async def get_by_subject_id(
        self,
        *,
        user_id: int,
        subject_id: int,
        db_session: AsyncSession | None = None,
    ) -> UserSuggestion | None:
        db_session = db_session or super().get_db().session
        response = await db_session.execute(
            select(self.model.recommended_user_ids).where((self.model.user_id == user_id)
            & (self.model.subject_id == subject_id))
        )

        return response.scalar_one_or_none()
    
    async def get_recommended_user_info(
        self,
        *,
        user_id: int,
        subject_id:int,
        db_session: AsyncSession | None = None,
    ):
        db_session = db_session or super().get_db().session
        query = text("""
            SELECT ranking.user_id, p.nickname, p.profile_image, ranking.top_values FROM(
                SELECT ranked_keys.user_id, ARRAY_AGG(keys) AS top_values FROM(
                    SELECT
                        user_id,
                        keys,
                        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY value DESC) AS rn
                    FROM (
                        SELECT
                            ss.user_id,
                            (json_each(ss.recommended_subject_ids)).key AS keys,
                            ((json_each(ss.recommended_subject_ids)).value)::text::int AS value
                        FROM
                            subject_suggestion as ss
                        WHERE
                            ss.user_id = ANY (ARRAY(
                                    SELECT recommended_user_ids 
                                    FROM user_suggestion 
                                    WHERE user_id=:user_id_param
                                    AND subject_id=:subject_id_param)
                            )
                    ) AS key_values 
                ) AS ranked_keys 
                WHERE rn <= 5
                GROUP BY ranked_keys.user_id
            ) AS ranking
            LEFT JOIN profile AS p
            ON ranking.user_id=p.user_id
        """)
       
        query = query.bindparams(
            user_id_param=user_id,
            subject_id_param=subject_id
        )
        response = await db_session.execute(query)

        return response.fetchall()

def get_community_repository() -> CommunityRepository:
    return CommunityRepository(UserSuggestion)