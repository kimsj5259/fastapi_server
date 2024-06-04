from datetime import timedelta
from fastapi import Depends

from redis.asyncio import Redis

from ...core.db.redis import get_redis_client
from ...core.schemas.common_schema import TokenType

from ..models.user_model import User


class TokenStorageService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def _generate_token_key(
        self, user_id: int, token_type: TokenType, provider_name: str | None = None
    ):
        if provider_name is None:
            return f"user:{user_id}:{token_type}"
        return f"user:{user_id}:{token_type}:{provider_name}"

    async def get_valid_tokens(
        self, user_id: int, token_type: TokenType, provider_name: str | None = None
    ):
        token_key = self._generate_token_key(user_id, token_type, provider_name)
        valid_tokens = await self.redis_client.smembers(token_key)
        return valid_tokens

    async def add_token_to_redis(
        self,
        user: User,
        token: str,
        token_type: TokenType,
        expire_time: int | None = None,
        provider_name: str | None = None,
    ):
        token_key = self._generate_token_key(user.id, token_type, provider_name)
        valid_tokens = await self.get_valid_tokens(user.id, token_type, provider_name)
        await self.redis_client.sadd(token_key, token)
        if not valid_tokens:
            await self.redis_client.expire(token_key, timedelta(minutes=expire_time))

    async def add_valid_token_to_redis(
        self,
        user: User,
        token: str,
        token_type: TokenType,
        expire_time: int | None = None,
        provider_name: str | None = None,
    ):
        valid_tokens = await self.get_valid_tokens(user.id, token_type, provider_name)
        if valid_tokens:
            await self.add_token_to_redis(
                user, token, token_type, expire_time, provider_name
            )

    async def delete_tokens(
        self, user: User, token_type: TokenType, provider_name: str | None = None
    ):
        token_key = self._generate_token_key(user.id, token_type, provider_name)
        valid_tokens = await self.redis_client.smembers(token_key)
        if valid_tokens is not None:
            await self.redis_client.delete(token_key)


def get_token_storage_service(
    redis_client: Redis = Depends(get_redis_client),
) -> TokenStorageService:
    return TokenStorageService(redis_client=redis_client)
