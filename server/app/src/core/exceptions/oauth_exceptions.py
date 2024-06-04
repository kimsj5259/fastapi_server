from fastapi import HTTPException, status


class InvalidToken(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid external OAuth token.",
        )


class InvalidAuthorizationCode(Exception):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid external OAuth authorization code.",
        )
