# Створюємо репозиторій користувача
from sqlalchemy import select, update

from src.database.db import sessionmanager
from src.database.models import User, Post, PostTag, Tag
from src.database.enums import Role
from src.schemas.posts import PostResponce, PostsRequest

async def create_post(body: dict) -> int|None:
    async with sessionmanager.session() as session:
        async with session.begin():
            new_post = Post(image_url=body.get('image_url'),
                            description=body.get('description'),
                            user_id=body.get('user_id')) # the same **body
            session.add(new_post)
            await session.flush()
            post_id = new_post.id
        print(f"Post {body.get('image_url')} added successfully!")
        return post_id



