# Створюємо репозиторій користувача
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.database.db import sessionmanager
from src.database.models import User
from src.schemas.users import UserModel


async def get_user_by_email(email: str) -> User:
    async with sessionmanager.session() as session:
        query = select(User).where(User.email == email)
        print(query)
        result = await session.execute(query)
        print(result)
        return result.scalar()


async def create_user(body: UserModel) -> dict:
    async with sessionmanager.session() as session:
        async with session.begin():
            new_user = User(email=body.email, password=body.password)
            session.add(new_user)
            await session.flush()
            user_id = new_user.id
            user_email = new_user.email
            created_at = new_user.created_at
            avatar = new_user.avatar
        print(f"User {body.email} added successfully!")
        return {"id": user_id, "email": user_email, "created_at": created_at, "avatar": avatar}


async def update_token(user: User, token: str | None) -> None:
    async with sessionmanager.session() as session:
        stmt = (
            update(User)
            .where(User.id == user.id)     # ✅ filter by user!
            .values(refresh_token=token)
        )
        await session.execute(stmt)
        await session.commit()

async def confirmed_email(email: str) -> None:
    async with sessionmanager.session() as session:
        stmt = (
            update(User)
            .where(User.email == email)     # ✅ filter by user!
            .values(confirmed=True)
        )
        await session.execute(stmt)
        await session.commit()

async def update_avatar(email, url: str) -> None:
    async with sessionmanager.session() as session:
        stmt = (
            update(User)
            .where(User.email == email)     # ✅ filter by user!
            .values(avatar=url)
        )
        await session.execute(stmt)
        await session.commit()
    user=await get_user_by_email(email)
    user_id = user.id
    user_email = user.email
    created_at = user.created_at
    avatar = user.avatar
    return {"id": user_id, "email": user_email, "created_at": created_at, "avatar": avatar}


