from fastapi import APIRouter

from .views import journal_view, mood_view, auth_view, role_view, user_view, community_view


api_router = APIRouter()

api_router.include_router(auth_view.router, prefix="/auth", tags=["auth"])
api_router.include_router(role_view.router, prefix="/role", tags=["role"])
api_router.include_router(user_view.router, prefix="/user", tags=["user"])
api_router.include_router(journal_view.router, prefix="/journal", tags=["journal"])
api_router.include_router(mood_view.router, prefix="/mood", tags=["mood"])
api_router.include_router(community_view.router, prefix="/community", tags=["community"])
