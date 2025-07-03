from datetime import timedelta
import secrets

from jose import jwt, ExpiredSignatureError
from loguru import logger

from pydantic import EmailStr
from pydantic import ValidationError
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from ..repositories.profile_repository import ProfileRepository, get_profile_repository

from ...core.utils.auth.security import (
    create_token,
    get_password_hash,
    verify_password,
    ALGORITHM,
)
from ...core.common_deps import get_current_user
from ...core.config import settings
from ...core.schemas.common_schema import TokenType, OauthProvider
from ...core.schemas.response_schema import (
    IGetResponseBase,
    IPostResponseBase,
    create_response,
)

from ..deps.auth_deps import access_oauth_client
from ..services.oauth_client import OAuthClient
from ..schemas.auth_schema import (
    ExternalCallbackResponse,
    TokenRead,
    Token,
    RefreshToken,
)
from ..models.user_model import User
from ..repositories.user_repository import UserRepository, get_user_repository
from ..schemas.user_schema import IUserCreate
from ..schemas.profile_schema import IProfileCreate
from ..services.token_service import (
    TokenStorageService,
    get_token_storage_service,
)

from ...core.exceptions.common_exception import UnauthorizedException
from ...core.exceptions.http_error import HttpErrorEnum

router = APIRouter()

"""
OAuth Related
"""


@router.get("/external/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def login_external_provider(
    oauth_client: OAuthClient = Depends(access_oauth_client),
):
    state = secrets.token_urlsafe(32)
    login_url = oauth_client.get_oauth_login_url(state=state)
    return RedirectResponse(login_url)


# TODO: 403에 대해서 swagger 추가
@router.get("/external/callback")
async def external_provider_callback(
    code: str,
    state: str | None = None,
    oauth_client: OAuthClient = Depends(access_oauth_client),
    user_repository: UserRepository = Depends(get_user_repository),
    profile_repository: ProfileRepository = Depends(get_profile_repository),
    token_service: TokenStorageService = Depends(get_token_storage_service),
) -> IGetResponseBase[ExternalCallbackResponse]:
    token_response = await oauth_client.get_tokens(code, state)

    if oauth_client.provider_name == OauthProvider.kakao:
        user_info = await oauth_client.get_user_info(access_token=token_response.access_token)

        user = await user_repository.get_by_provider_user_id(provider_user_id=user_info.id)

        # provider_user_id가 존재하지 않는 유저라면 새로 생성해서 저장
        if user is None:
            # TODO: 카카오의 닉네임이 아닌 "실제 이름"으로 적용
            new_user = IUserCreate(
                user_name=user_info.kakao_account.profile.nickname,
                oauth_provider=oauth_client.provider_name,
                provider_user_id=user_info.id,
                email=user_info.kakao_account.email,
                # gender=user_info.kakao_account.gender,
                # birth_date=user_info.kakao_account.birthday,
                profile_completion=False,
            )
            user = await user_repository.create_with_role(obj_in=new_user)

    elif oauth_client.provider_name == OauthProvider.apple:
        public_keys = await oauth_client.get_public_key()
        logger.debug(f'Public keys {public_keys}')
        matched_kid = jwt.get_unverified_header(token_response.id_token)["kid"]
        matched_key = public_keys[matched_kid]

        logger.info(matched_key)

        decoded = jwt.decode(
            token_response.id_token,
            key=matched_key,
            algorithms=["RS256"],
            audience=settings.APPLE_CLIENT_ID,
            access_token=token_response.access_token,
        )

        logger.info(f"DECODED :: {decoded}")

        user = await user_repository.get_by_provider_user_id(
            provider_user_id=decoded["sub"]
        )

        # provider_user_id가 존재하지 않는 유저라면 새로 생성해서 저장
        # TODO: 애플 유저 이름 얻는 로직 추가 필요
        if user is None:
            new_user = IUserCreate(
                user_name="",
                oauth_provider=oauth_client.provider_name,
                provider_user_id=decoded["sub"],
                email=decoded["email"],
                profile_completion=False,
            )
            user = await user_repository.create_with_role(obj_in=new_user)

    else:
        raise NotImplementedError("Other providers not implemented!")

    profile = await profile_repository.get_by_id(user_id=user.id)
    if profile is None:
        new_profile = IProfileCreate(user_id=user.id)
        profile = await profile_repository.create(obj_in=new_profile)

    # 외부 OAuth provider 에서 온 token을 redis에 저장 (api 재활용을 위해)
    await token_service.add_valid_token_to_redis(
        user,
        token_response.access_token,
        TokenType.ACCESS,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        oauth_client.provider_name,
    )
    await token_service.add_valid_token_to_redis(
        user,
        token_response.refresh_token,
        TokenType.REFRESH,
        settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        oauth_client.provider_name,
    )

    # 자체 OAuth token 생성 후 redis에 저장
    access_token = create_token(user.id, TokenType.ACCESS)
    refresh_token = create_token(user.id, TokenType.REFRESH)

    await token_service.add_valid_token_to_redis(user, access_token, TokenType.ACCESS)
    await token_service.add_valid_token_to_redis(user, refresh_token, TokenType.REFRESH)

    data = ExternalCallbackResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=user,
        profile=profile,
    )

    return create_response(
        data=data, message=f"Logged in correctly via {oauth_client.provider_name}"
    )


@router.post("/refresh-access-token", status_code=status.HTTP_201_CREATED)
async def get_new_access_token(
    user_repository: UserRepository = Depends(get_user_repository),
    body: RefreshToken = Body(...),
    token_service: TokenStorageService = Depends(get_token_storage_service),
) -> IPostResponseBase[TokenRead]:
    """
    Gets a new access token using the refresh token for future requests
    """
    try:
        payload = jwt.decode(body.refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise UnauthorizedException(HttpErrorEnum.REFRESH_EXPIRED, "refresh token is expired")
    except (jwt.JWTError, ValidationError):
        raise UnauthorizedException(HttpErrorEnum.NOT_VERIFIED, "refresh token is not verified")

    if payload["type"] == "refresh":
        user_id = int(payload["sub"])
        valid_refresh_tokens = await token_service.get_valid_tokens(
            user_id, TokenType.REFRESH
        )
        if valid_refresh_tokens and body.refresh_token not in valid_refresh_tokens:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token invalid"
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        user = await user_repository.get(id=user_id)
        if user.is_active:
            access_token = create_token(
                payload["sub"], TokenType.ACCESS, expires_delta=access_token_expires
            )
            valid_access_get_valid_tokens = await token_service.get_valid_tokens(
                user.id, TokenType.ACCESS
            )
            if valid_access_get_valid_tokens:
                await token_service.add_token_to_redis(
                    user,
                    access_token,
                    TokenType.ACCESS,
                    settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                )
            return create_response(
                data=TokenRead(access_token=access_token, token_type="bearer"),
                message="Access token generated correctly",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User inactive"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect token"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user()),
    token_service: TokenStorageService = Depends(get_token_storage_service),
):
    await token_service.delete_tokens(current_user, TokenType.ACCESS)
    await token_service.delete_tokens(current_user, TokenType.REFRESH)

    return create_response(data=None, message=f"Logged out {current_user.id} correctly")


"""
Below Currently Deprecated
"""


@router.post("/login", deprecated=True)
async def login(
    email: EmailStr = Body(...),
    password: str = Body(...),
    user_repository: UserRepository = Depends(get_user_repository),
    token_service: TokenStorageService = Depends(get_token_storage_service),
) -> IPostResponseBase[Token]:
    """
    Login for all users
    """
    user = await user_repository.authenticate(email=email, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or Password incorrect",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is inactive"
        )

    access_token = create_token(user.id, TokenType.ACCESS)
    refresh_token = create_token(user.id, TokenType.REFRESH)

    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=user,
    )

    await token_service.add_valid_token_to_redis(user, access_token, TokenType.ACCESS)
    await token_service.add_valid_token_to_redis(user, refresh_token, TokenType.REFRESH)

    return create_response(data=data, message="Login correctly")


@router.post("/change-password", deprecated=True)
async def change_password(
    user_repository: UserRepository = Depends(get_user_repository),
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_user()),
    token_service: TokenStorageService = Depends(get_token_storage_service),
) -> IPostResponseBase[Token]:
    """
    Change password
    """
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Current Password"
        )

    if verify_password(new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New Password should be different that the current one",
        )

    new_hashed_password = get_password_hash(new_password)
    await user_repository.update(
        obj_current=current_user, obj_new={"hashed_password": new_hashed_password}
    )

    access_token = create_token(
        current_user.id,
        TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_token(
        current_user.id,
        TokenType.REFRESH,
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )

    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=current_user,
    )

    await token_service.delete_tokens(current_user, TokenType.ACCESS)
    await token_service.delete_tokens(current_user, TokenType.REFRESH)
    await token_service.add_token_to_redis(
        current_user,
        access_token,
        TokenType.ACCESS,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    await token_service.add_token_to_redis(
        current_user,
        refresh_token,
        TokenType.REFRESH,
        settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    return create_response(data=data, message="New password generated")


@router.post("/access-token", deprecated=True)
async def login_access_token(
    user_repository: UserRepository = Depends(get_user_repository),
    form_data: OAuth2PasswordRequestForm = Depends(),
    token_service: TokenStorageService = Depends(get_token_storage_service),
) -> TokenRead:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await user_repository.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token = create_token(
        user.id,
        TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    valid_access_tokens = await token_service.get_valid_tokens(
        user.id, TokenType.ACCESS
    )
    if valid_access_tokens:
        await token_service.add_token_to_redis(
            user,
            access_token,
            TokenType.ACCESS,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    return {"access_token": access_token, "token_type": "bearer"}


#### 잘생긴 진형님