from typing import Any
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext

from ...schemas.common_schema import TokenType

from ...config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(str.encode(settings.ENCRYPT_KEY))

ALGORITHM = "HS256"


def create_token(
    subject: str | Any, token_type: TokenType, expires_delta: timedelta | None = None
):
    default_expire_delta_map = {
        TokenType.ACCESS: settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        TokenType.REFRESH: settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    }

    delta = (
        expires_delta
        if expires_delta
        else timedelta(minutes=default_expire_delta_map.get(token_type, 0))
    )

    to_encode = {
        "exp": datetime.utcnow() + delta,
        "sub": str(subject),
        "type": token_type.value,
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


"""
Currently unused
"""


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_data_encrypt(data) -> str:
    data = fernet.encrypt(data)
    return data.decode()


def get_content(variable: str) -> str:
    return fernet.decrypt(variable.encode()).decode()
