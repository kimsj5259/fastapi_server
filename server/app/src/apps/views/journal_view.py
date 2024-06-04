from datetime import date
import itertools
import operator
from typing import Any, Annotated, Optional, List

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Body, Request
from fastapi_pagination import Params

from ..models.user_model import User
from ..schemas.role_schema import IRoleEnum
from ...core.base_service import S3Events, S3_BASE_URL
from ...core.common_deps import get_current_user
from ...core.exceptions.common_exception import IdNotFoundException
from ...core.schemas.response_schema import (
    IGetResponsePaginated,
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase,
    IDeleteResponseBase,
    create_response,
    create_list_response,
)

from ..repositories.journal_respository import JournalRepository, get_journal_repository
from ..schemas.journal_schemas import IJournalCreate, IJournalRead, ListByMonthResponse, IJournalSpecifiedDateRead
from ..models.journal_model import Journal
from ..deps.journal_deps import s3_journal_middleware
from ..models.journal_model import WithWhomEnum, TopicEnum


router = APIRouter()

@router.post("/sibel") # sibel 시험용 POST api 
async def sibel_health(request: Request):
    data = await request.json()
    return data


@router.post("")
async def create_journal(
    # new_journal: IjournalCreate = Depends(checker),
    with_whom: Annotated[WithWhomEnum, Body()],
    topic: Annotated[list[Optional[TopicEnum]], Body()],
    reason: Annotated[str, Body()],
    action_from_emotion: Annotated[str, Body()],
    context: Annotated[str, Body()],
    journal_time_at: Annotated[date, Body()],
    mood_macro_status_id: Annotated[int, Body()],
    mood_micro_status_id: Annotated[int, Body()],
    files: List[UploadFile] = File(None),
    journal_repository: JournalRepository = Depends(get_journal_repository),
    current_user: User = Depends(get_current_user()),
) -> IPostResponseBase[IJournalCreate]:
    """
    Creates a new journal
    """
    new_journal = Journal(
        **{
            "with_whom": with_whom,
            "topic": topic,
            "reason": reason,
            "action_from_emotion": action_from_emotion,
            "context": context,
            "user_id": current_user.id,
            "journal_time_at": journal_time_at,
            "mood_macro_status_id": mood_macro_status_id,
            "mood_micro_status_id": mood_micro_status_id,
        }
    )

    ##### S3 image create #####
    if files:
        s3_obj_key_list = await s3_journal_middleware(
            files=files, user_id=current_user.id
        )

        new_journal.images = s3_obj_key_list

    journal = await journal_repository.create(obj_in=new_journal)

    if journal.images:
        journal.images = {
            "base_url": S3_BASE_URL,  # base_url이 생기므로 일일히 s3 obj key와 결합할 필요강 없어짐.
            "detail_path": s3_obj_key_list,
        }

    return create_response(data=journal)


@router.get("")
async def journal_start_to_end_date(
    start_date: date,
    end_date: date,
    journal_repository: JournalRepository = Depends(get_journal_repository),
    current_user: User = Depends(get_current_user()),
) -> IGetResponseBase[list[IJournalSpecifiedDateRead]]:
    """
    Get journal list from start date to end date
    """
    query = await journal_repository.get_by_specified_date(
        user_id=current_user.id, 
        start_date=start_date, 
        end_date=end_date
    )
    
    return create_response(data=query)


@router.get("/month")
async def read_journal_list(
    date: date,
    journal_repository: JournalRepository = Depends(get_journal_repository),
    current_user: User = Depends(get_current_user()),
) -> IGetResponseBase[list[ListByMonthResponse]]:
    """
    Get journal list by month
    """

    def group_data(data: list, key: Any):
        sorted_data = sorted(data, key=key)
        return itertools.groupby(sorted_data, key=key)

    journal_list = await journal_repository.get_by_month(user_id=current_user.id, date=date)
    journal_list = [journal.dict() for journal in journal_list]

    date_grouped_data = group_data(journal_list, key=operator.itemgetter("journal_time_at"))

    # TODO: 필요에 따라 최적화
    result = []
    for key, date_group in date_grouped_data:
        mood_date_grouped_data = group_data(
            list(date_group),
            key=lambda x: (x["mood_micro_status_id"], x["mood_macro_status_id"]),
        )

        mood_key_len = []
        for mood_key, mood_value in mood_date_grouped_data:
            diaries = sorted(list(mood_value), key=lambda x: x["journal_time_at"])
            journal_recent_created_at = diaries[-1]["journal_time_at"]
            journal_len = len(diaries)

            mood_key_len.append(
                {
                    "mood_micro_status_id": mood_key[0],
                    "mood_macro_status_id": mood_key[1],
                    "journal_time_at": journal_recent_created_at,
                    "length": journal_len,
                }
            )

        sorted_mood_key = sorted(mood_key_len, key=lambda x: -x["length"])

        representing_mood = sorted_mood_key[0]

        mood_value = {
            "journal_time_at": str(key),
            "mood_micro_status_id": representing_mood["mood_micro_status_id"],
            "mood_macro_status_id": representing_mood["mood_macro_status_id"],
        }

        result.append(mood_value)

    return create_response(data=result)


@router.get("/detail")
async def read_one_journal(
    journal_id: int,
    journal_repository: JournalRepository = Depends(get_journal_repository),
    current_user: User = Depends(get_current_user()),
) -> IGetResponseBase[IJournalCreate]:
    """
    Get data from a journal
    """
    selected_journal = await journal_repository.get(id=journal_id)

    if not selected_journal:
        raise IdNotFoundException(Journal, id=journal_id)

    if selected_journal.images:
        selected_journal.images = {
            "base_url": S3_BASE_URL,
            "detail_path": selected_journal.images,
        }

    return create_response(data=selected_journal)


@router.put("")  # TODO: 아직 context만 수정 가능하다던가, 아무거나 수정가능하다거나 정해지지 않아서 러프하게 짜놓음
async def update_journal(
    journal_id: int,
    with_whom: Annotated[WithWhomEnum, Body()],
    topic: Annotated[list[Optional[TopicEnum]], Body()],
    reason: Annotated[str, Body()],
    action_from_emotion: Annotated[str, Body()],
    context: Annotated[str, Body()],
    journal_time_at: Annotated[date, Body()],
    mood_macro_status_id: Annotated[int, Body()],
    mood_micro_status_id: Annotated[int, Body()],
    images: list = Body(None),
    files: List[UploadFile] = File(None),
    journal_repository: JournalRepository = Depends(get_journal_repository),
    current_user: User = Depends(get_current_user()),
) -> IPutResponseBase[IJournalCreate]:
    """
    Update data from a journal
    """
    selected_journal = await journal_repository.get(id=journal_id)

    if not selected_journal:
        raise IdNotFoundException(Journal, id=journal_id)

    updated_journal = Journal(
        **{
            "with_whom": with_whom,
            "topic": topic,
            "reason": reason,
            "action_from_emotion": action_from_emotion,
            "context": context,
            "user_id": current_user.id,
            "journal_time_at": journal_time_at,
            "mood_macro_status_id": mood_macro_status_id,
            "mood_micro_status_id": mood_micro_status_id,
            "images": images if images else None,
        }
    )

    ##### S3 image create #####
    if files:
        # S3Events.delete_images(files=selected_journal.images) # delete all images in journal first
        s3_obj_key_list = await s3_journal_middleware(
            files=files, 
            user_id=current_user.id
        )

        if images:  # images에 기존 키값이 있다면 새로 받은 파일과 합쳐서 리스트
            if len(updated_journal.images) + len(s3_obj_key_list) > 4:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="journal images cannot exceed maximum 4",
                )
            updated_journal.images = updated_journal.images + s3_obj_key_list
        else:
            updated_journal.images = s3_obj_key_list

    updated_context = await journal_repository.update(
        obj_current=selected_journal, obj_new=updated_journal
    )

    if updated_context.images:
        updated_context.images = {
            "base_url": S3_BASE_URL,
            "detail_path": updated_context.images,
        }

    return create_response(data=updated_context)


@router.delete("")
async def remove_journal(
    journal_id: int,
    journal_repository: JournalRepository = Depends(get_journal_repository),
    current_user: User = Depends(get_current_user()),
) -> IDeleteResponseBase[IJournalRead]:
    """
    Delete a journal
    """
    selected_journal = await journal_repository.get(id=journal_id)

    if not selected_journal:
        raise IdNotFoundException(Journal, id=journal_id)

    if selected_journal.images:
        S3Events().delete_images(
            files=selected_journal.images
        )  # 해당 다이어리의 S3 images 함께 삭제

    journal = await journal_repository.remove(id=journal_id)
    return create_response(data=journal, message="Selected journal removed")
