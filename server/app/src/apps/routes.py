from fastapi import APIRouter

from .routers import journal_router, mood_router, auth_router, role_router, user_router, community_router


api_router = APIRouter()

api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(role_router.router, prefix="/role", tags=["role"])
api_router.include_router(user_router.router, prefix="/user", tags=["user"])
api_router.include_router(journal_router.router, prefix="/journal", tags=["journal"])
api_router.include_router(mood_router.router, prefix="/mood", tags=["mood"])
api_router.include_router(community_router.router, prefix="/community", tags=["community"])
