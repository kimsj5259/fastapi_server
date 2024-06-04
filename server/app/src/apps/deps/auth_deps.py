from typing import Annotated
from fastapi import HTTPException, Query, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..services.oauth_client import OAuthClient, kakao_client, apple_client

security = HTTPBearer()


def access_oauth_client(
    provider: Annotated[str, Query(..., regex="apple|kakao|naver")] = "kakao"
) -> OAuthClient:
    if provider == "naver":
        return NotImplementedError("Naver social login not implemented.")
    elif provider == "kakao":
        return kakao_client
    elif provider == "apple":
        return apple_client
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Not a valid oauth provider",
        )


def obtain_authorization_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    token = credentials.credentials
    if not token or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
