from typing import Literal, Callable
from datetime import datetime
from urllib import parse
import ssl
import certifi
from jose import jwt
from jose import jwk
import boto3
from botocore.exceptions import ClientError

import aiohttp
from loguru import logger

from ...core.config import settings
from ...core.exceptions.oauth_exceptions import InvalidAuthorizationCode, InvalidToken

from ..schemas.auth_schema import (
    OAuthToken,
    OAuthTokenBase,
    KakaoOAuthUserInfo,
)


SupportedProviderType = Literal["kakao", "apple"]


class OAuthClient:
    def __init__(
        self,
        provider_name: SupportedProviderType,
        client_id: str,
        client_secret_func: Callable,
        redirect_uri: str,
        authentication_uri: str,
        resource_uri: str,
        verify_uri: str,
    ):
        self.provider_name = provider_name
        self._client_id = client_id
        self._client_secret_func = client_secret_func
        self._redirect_uri = redirect_uri
        self._authentication_uri = authentication_uri
        self._resource_uri = resource_uri
        self._verify_uri = verify_uri
        self._header_name = "Authorization"
        self._header_type = "Bearer"

    def _get_connector_for_ssl(self) -> aiohttp.TCPConnector:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        return aiohttp.TCPConnector(ssl=ssl_context)

    async def _request_get_to(self, url, headers=None) -> dict | None:
        conn = self._get_connector_for_ssl()
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(url, headers=headers) as resp:
                return None if resp.status != 200 else await resp.json()

    async def _request_post_to(self, url, payload=None) -> dict | None:
        conn = self._get_connector_for_ssl()
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.post(url, data=payload) as resp:
                return None if resp.status != 200 else await resp.json()

    def get_oauth_login_url(self, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "state": state,
        }
        query_param = parse.urlencode(params, doseq=True)

        return f"{self._authentication_uri}/authorize?{query_param}"

    async def get_tokens(self, code: str, state: str) -> OAuthToken:
        logger.info(f'get_tokens {code} {state}')
        tokens = await self._request_post_to(
            url=f"{self._authentication_uri}/token",
            payload={
                "client_id": self._client_id,
                "client_secret": self._client_secret_func(),
                "grant_type": "authorization_code",
                "code": code,
                "state": state,
            },
        )

        logger.info(tokens)

        if tokens is None:
            raise InvalidAuthorizationCode()

        if tokens.get("access_token") is None or tokens.get("refresh_token") is None:
            raise InvalidAuthorizationCode()

        return OAuthToken(**tokens)

    async def get_public_key(self):
        response = await self._request_get_to(url=f"{self._authentication_uri}/keys")
        public_keys = {
            key["kid"]: jwk.construct(key).to_dict() for key in response["keys"]
        }
        return public_keys

    async def refresh_access_token(self, refresh_token: str) -> OAuthTokenBase:
        tokens = await self._request_post_to(
            url=f"{self._authentication_uri}/token",
            payload={
                "client_id": self._client_id,
                "client_secret": self._client_secret_func(),
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        if tokens is None:
            raise InvalidToken()

        return OAuthTokenBase(**tokens)

    async def get_user_info(self, access_token: str) -> KakaoOAuthUserInfo:
        headers = {self._header_name: f"{self._header_type} {access_token}"}
        user_info = await self._request_get_to(url=self._resource_uri, headers=headers)
        if user_info is None:
            raise InvalidToken()

        logger.debug(f"USER INFO ::: {user_info}")

        return KakaoOAuthUserInfo(**user_info)

    async def is_authenticated(self, access_token: str) -> bool:
        headers = {self._header_name: f"{self._header_type} {access_token}"}
        res = await self._request_get_to(url=self._verify_uri, headers=headers)
        return res is not None

    # async def logout(self, access_token: str, target_id: str):
    #     headers = {self._header_name: f"{self._header_type} {access_token}"}
    #     res = await self._request_post_to(
    #         url="https://kapi.kakao.com/v1/user/logout",
    #         headers=headers,
    #         payload={
    #             "target_id_type": "user_id",
    #             "target_id": target_id,
    #         },
    #     )
    #     return res


def get_kakao_client_secret_id():
    return settings.KAKAO_CLIENT_SECRET_ID


kakao_client = OAuthClient(
    provider_name="kakao",
    client_id=settings.KAKAO_CLIENT_ID,
    client_secret_func=get_kakao_client_secret_id,
    redirect_uri=settings.KAKAO_REDIRECT_URI,
    authentication_uri="https://kauth.kakao.com/oauth",
    resource_uri="https://kapi.kakao.com/v2/user/me",
    verify_uri="https://kapi.kakao.com/v1/user/access_token_info",
)

def fetch_apple_auth_from_secret_manager():

    secret_name = settings.APPLE_AUTH_KEY

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=settings.AWS_DEFAULT_REGION
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']

    return secret

def get_apple_client_secret_id():
    logger.info('get_apple_client_secret_id')
    private_key = fetch_apple_auth_from_secret_manager()

    validity_minutes = 20
    timestamp_now = int(datetime.now().timestamp())
    timestamp_exp = timestamp_now + (60 * validity_minutes)

    data = {
        "iss": settings.APPLE_TEAM_ID,
        "iat": timestamp_now,
        "exp": timestamp_exp,
        "aud": "https://appleid.apple.com",
        "sub": settings.APPLE_CLIENT_ID,
    }
    token = jwt.encode(
        data,
        private_key,
        algorithm="ES256",
        headers={"kid": settings.APPLE_KEY_ID},
    )

    
    return token


apple_client = OAuthClient(
    provider_name="apple",
    client_id=settings.APPLE_CLIENT_ID,
    client_secret_func=get_apple_client_secret_id,
    redirect_uri=settings.APPLE_REDIRECT_URI,
    authentication_uri="https://appleid.apple.com/auth",
    resource_uri="",
    verify_uri="",
)
