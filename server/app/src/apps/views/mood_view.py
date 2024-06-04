from typing import Annotated
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Query,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi_pagination import Params

from ...core.exceptions.common_exception import IdNotFoundException
from ...core.schemas.response_schema import (
    IGetResponsePaginated,
    create_response,
    create_list_response,
)

from ..models.user_model import User
from ...core.common_deps import get_current_user
from ..schemas.mood_schemas import IMoodMicroRead
from ..repositories.mood_repository import (
    MoodMicroStatusRepository,
    get_mood_micro_repository,
)


router = APIRouter()


@router.get("/macro_and_micro_id")
async def get_mood_macro(
    params: Params = Depends(),
    current_user: User = Depends(get_current_user()),
    mood_micro_repository: MoodMicroStatusRepository = Depends(
        get_mood_micro_repository
    ),
) -> IGetResponsePaginated[IMoodMicroRead]:
    """
    Get mood macro & micro id
    """
    query = await mood_micro_repository.find_mood_macro_id_with_micro_id()
    mood_micro_list = await mood_micro_repository.get_multi_paginated(
        query=query, params=params
    )

    return create_list_response(data=mood_micro_list)
