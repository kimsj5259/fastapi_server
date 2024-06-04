import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

from ..db.session import SessionLocal

from ..config import settings
from ...apps.schemas.role_schema import IRoleCreate
from ...apps.schemas.user_schema import IUserCreate
from ...apps.repositories.user_repository import get_user_repository
from ...apps.repositories.role_repository import get_role_repository


roles: list[IRoleCreate] = [
    IRoleCreate(name="admin", description="Admin role"),
    IRoleCreate(name="founder", description="Founder role"),
    IRoleCreate(name="user", description="User role"),
]


users: list[dict[str, str | IUserCreate]] = [
    {
        "data": IUserCreate(
            user_name="Admin FastAPI",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email=settings.FIRST_SUPERUSER_EMAIL,
            age=99,
        ),
        "role": "admin",
    },
    {
        "data": IUserCreate(
            user_name="Founder FastAPI",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email="founder@example.com",
            age=99,
        ),
        "role": "founder",
    },
    {
        "data": IUserCreate(
            user_name="User FastAPI",
            password=settings.FIRST_SUPERUSER_PASSWORD,
            email="user@example.com",
            age=99,
        ),
        "role": "user",
    },
]


async def init_db(db_session: AsyncSession) -> None:
    role_repository = get_role_repository()
    user_repository = get_user_repository()

    for role in roles:
        role_current = await role_repository.get_role_by_name(
            name=role.name, db_session=db_session
        )
        if not role_current:
            await role_repository.create(obj_in=role, db_session=db_session)

    for user in users:
        current_user = await user_repository.get_by_email(
            email=user["data"].email, db_session=db_session
        )
        role = await role_repository.get_role_by_name(
            name=user["role"], db_session=db_session
        )
        if not current_user:
            user["data"].role_id = role.id
            await user_repository.create_with_role(
                obj_in=user["data"], db_session=db_session
            )


async def create_init_data() -> None:
    async with SessionLocal() as session:
        await init_db(session)


async def main() -> None:
    await create_init_data()


if __name__ == "__main__":
    asyncio.run(main())
