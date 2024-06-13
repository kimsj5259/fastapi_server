import logging
from collections.abc import AsyncGenerator

from jose import jwt, ExpiredSignatureError

from pydantic import ValidationError
from fastapi import Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from .utils.auth import security
from .config import settings
from .db.session import SessionLocal
from .schemas.common_schema import TokenType

from ..apps.deps.auth_deps import obtain_authorization_token
from ..apps.models.user_model import User
from ..apps.repositories.user_repository import UserRepository, get_user_repository
from ..apps.services.token_service import (
    TokenStorageService,
    get_token_storage_service,
)
from .exceptions.common_exception import UnauthorizedException, BadRequestException
from .exceptions.http_error import HttpErrorEnum

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


def get_current_user(required_roles: list[str] = None) -> User:
    async def current_user(
        user_repository: UserRepository = Depends(get_user_repository),
        access_token: str = Depends(obtain_authorization_token),
        token_service: TokenStorageService = Depends(get_token_storage_service),
    ) -> User:
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
        except ExpiredSignatureError:
            raise UnauthorizedException(HttpErrorEnum.ACCESS_EXPIRED, "access token is expired")
        except (jwt.JWTError, ValidationError):
            raise UnauthorizedException(HttpErrorEnum.NOT_VERIFIED, "access token is not verified")
        
        try:
            user_id = int(payload["sub"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user type/syntax"
            )

        valid_access_tokens = await token_service.get_valid_tokens(
            user_id, TokenType.ACCESS
        )
        if valid_access_tokens and access_token not in valid_access_tokens:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user: User = await user_repository.get(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not user.is_active:
            raise BadRequestException(HttpErrorEnum.INACTIVE_USER, "Inaction User")

        if required_roles:
            is_valid_role = False
            for role in required_roles:
                if role == user.role.name:
                    is_valid_role = True

            if not is_valid_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"""Role "{required_roles}" is required for this action""",
                )

        return user

    return current_user
