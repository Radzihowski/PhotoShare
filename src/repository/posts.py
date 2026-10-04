# Створюємо репозиторій користувача
from sqlalchemy import select, exists, update, inspect, desc
from sqlalchemy.orm import selectinload

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

async  def delete_post(post_id:int, user_id:int) -> int:
    async with sessionmanager.session() as session:
        async with session.begin():
            query = select(exists().where(Post.id == post_id, Post.user_id == user_id, Post.is_deleted == False))
            print(query)
            result = await session.execute(query)
            print(result)
            is_exist =  result.scalar()
            print(is_exist)
            if is_exist == True:
                query = (
                    update(Post)
                    .where(Post.id == post_id, Post.user_id == user_id, Post.is_deleted == False)
                    .values(is_deleted=True)
                )
                print(query)
                result = await session.execute(query)
                print(result)
                await session.commit()
                return result.rowcount
            else:
                return 0

async def update_post(body: dict) -> int|None:
    async with sessionmanager.session() as session:
        async with session.begin():
            query = select(exists().where(Post.id == body["post_id"], Post.user_id == body["user_id"], Post.is_deleted == False))
            print(query)
            result = await session.execute(query)
            print(result)
            is_exist =  result.scalar()
            print(is_exist)
            if is_exist == True:
                query = (
                    update(Post)
                    .where(Post.id == body["post_id"], Post.user_id == body["user_id"], Post.is_deleted == False)
                    .values(description=body["description"])
                )
                print(query)
                result = await session.execute(query)
                print(result)
                await session.commit()
                return  200
            else:
                return 404


def to_dict(obj) -> dict:
    return {attr.key: getattr(obj, attr.key) for attr in inspect(obj).mapper.column_attrs}


async def get_post(post_id:int, user_id:int) -> dict|None:
    async with sessionmanager.session() as session:
        async with session.begin():
            query = (
                select(Post)
                .options(selectinload(Post.tags))
                .where(Post.id == post_id, Post.user_id == user_id, Post.is_deleted == False)
            )
            print(query)
            result = await session.execute(query)
            print(result)
            record: Post|None = result.scalar()
            print(record)
            if record is None:
                return None
            else:
                post = to_dict(record)
                post["tags"] = [to_dict(tag) for tag in record.tags]
                return post

async def get_posts(user_id:int) -> list[dict]:
    async with sessionmanager.session() as session:
        async with session.begin():
            query = (
                select(Post)
                .options(selectinload(Post.tags))
                .where(Post.user_id == user_id, Post.is_deleted == False)
                .order_by(desc(Post.created_at))
            )
            print(query)
            result = await session.execute(query)
            print(result)
            records: list[Post] = result.scalars()
            print(records)
            posts = [to_dict(r) for r in records]
            for p in posts:
                for r in records:
                    if p["id"] == r.id:
                        p["tags"] = [to_dict(tag) for tag in r.tags]
                p.pop("is_deleted", None)
            return posts
