import sys
import logging
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Response, HTTPException

from fastapi_pagination import add_pagination
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from loguru import logger

from .core.config import settings
from .core.utils.lifespan import lifespan
from .core.constants.constant import PRODUCTION
from .core.log.custom_logging import CustomizeLogger
from .apps.routes import api_router as api_router_v1

echo = True
level = logging.DEBUG
openapi_url=f"{settings.API_V1_STR}/openapi.json"
if settings.APP_ENV == PRODUCTION:
    echo = False
    openapi_url = None
    level = logging.INFO
    
# Core Application Instance
app = FastAPI(
    title = settings.PROJECT_NAME,
    version = settings.API_VERSION,
    openapi_url = openapi_url,
    lifespan = lifespan,
)

# TODO: 어떤 로깅이 좋을지는 보면서 판단
# CustomizeLogger.customize_logging(level)
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{level}</green> <yellow>{name}</yellow> {message}", level=level)
logging.basicConfig(level=logging.INFO)

async def log_request_middleware(request: Request, call_next):
    if request.url.path[-1] != '/':
        logger.info(f"Received request: {request.method} {request.url}")
    
    response = await call_next(request)
    if request.url.path[-1] != '/':
        logger.info(f"Sent response: {response.status_code}")

    return response

# 미들웨어 등록
app.middleware("http")(log_request_middleware)

app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=settings.ASYNC_DATABASE_URI,
    engine_args={
        "echo": echo,
        "pool_pre_ping": True,
        "pool_size": settings.POOL_SIZE,
        "max_overflow": 64,
    },
)

# Set all CORS origins enabled
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
async def health_check():
    """
    Health Check endpoint
    """
    return {"status": "ok"}


# Add Routers
app.include_router(api_router_v1, prefix=settings.API_V1_STR)
add_pagination(app)

