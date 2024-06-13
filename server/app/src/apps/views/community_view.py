from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_pagination import Params

from ...core.base_repository import BaseRepository
from ...core.base_service import S3_BASE_URL
from ...core.common_deps import get_current_user
from ...core.schemas.response_schema import (
    IGetResponseBase,
    IGetResponsePaginated,
    create_response,
    create_list_response
)

from ..models.user_model import User
from ..models.community_model import SubjectSuggestion
from ..schemas.community_schema import ISubjectSuggestionRead, IUserSuggestionRead, IMatchedUserResponse
from ..repositories.community_repository import CommunityRepository, get_community_repository


router = APIRouter()


@router.get("/matched-subject")
async def matched_subject(
    current_user: User = Depends(get_current_user()),
) -> IGetResponseBase[ISubjectSuggestionRead]:
    """
    Get matched subject (updated by offline ML logic)
    """
    response = await BaseRepository(SubjectSuggestion).get_by_user_id(user_id=current_user.id, pagination=False)

    return create_response(data=response)


@router.get("/matched-user")
async def get_matched_users(
    subject_id: int,
    current_user: User = Depends(get_current_user()),
    community_repository: CommunityRepository = Depends(get_community_repository),
) -> IGetResponseBase[IMatchedUserResponse]:
    """
    Get matched user (updated by offline ML logic)
    """
    determine_recommend_user_is_empty_or_not = await community_repository.get_by_subject_id(user_id=current_user.id, subject_id=subject_id)
    
    if not determine_recommend_user_is_empty_or_not:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"no recommended user with the subject id {subject_id}",
        )

    top_five_subject_with_recommended_user = await community_repository.get_recommended_user_info(user_id=current_user.id, subject_id=subject_id)
    
    data = {"data": top_five_subject_with_recommended_user, 
            "base_url": S3_BASE_URL}

    return create_response(data=data)


@router.get("/matched-user-with-subject")
async def get_matched_users_for_each_subject(
    subject_id: int,
    community_repository: CommunityRepository = Depends(get_community_repository),
    current_user: User = Depends(get_current_user()),
) -> IGetResponseBase[IUserSuggestionRead]:
    """
    Get matched user for each subject(updated by offline ML logic everyday)
    """

    response = await community_repository.get_by_subject_id(user_id=current_user.id, subject_id=subject_id)

    return create_response(data=response)
