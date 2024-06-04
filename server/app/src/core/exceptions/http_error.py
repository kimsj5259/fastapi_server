from enum import Enum

class HttpErrorEnum(str, Enum):
    NO_DATA = "NO_DATA"
    NO_JWT = "NO_JWT"
    NOT_VERIFIED = "NOT_VERIFIED"
    ACCESS_EXPIRED = "ACCESS_EXPIRED"
    REFRESH_EXPIRED = "REFRESH_EXPIRED"
    INACTIVE_USER = "INACTIVE_USER"

class HttpErrorMessage(str, Enum):
    ACCESS_EXPIRED = "access token is expired"
    NOT_VERIFIED = "access token is not verified"
    REFRESH_EXPIRED = "refresh token is expired"
    