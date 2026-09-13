from uuid import uuid4

from src.utils.py_logger import get_logger
import cloudinary
import cloudinary.uploader
from src.conf.config import settings
from src.database.enums import Role
from src.services.rbac import RoleAccess

from fastapi import APIRouter, status, Query, UploadFile, File, Form, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_limiter.depends import RateLimiter
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.database.models import User
from src.conf.config import settings
from src.repository import posts as repository_posts

from src.schemas.posts import PostsRequest, PostResponce
from src.schemas.contacts import ContactRequest, ContactResponse
from src.services.contacts import ContactService

logger = get_logger(__name__)
router = APIRouter(prefix='/posts', tags=["posts"])
security = HTTPBearer()

@router.post('/create', status_code=status.HTTP_200_OK, response_model=PostResponce)
async def create_post(description: str | None = Form(None, max_length=2056), file: UploadFile = File(), current_user: User = Depends(RoleAccess(Role.USER))):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    public_id = f'PhotoShare/{current_user.id}/{uuid4().hex}'
    r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    src_url = r['secure_url']
    payload:dict = {"description": description, "image_url": src_url, "user_id": current_user.id}
    print(payload)
    print(type(payload))
    post_id = await repository_posts.create_post(body=payload)
    return PostResponce(id=post_id)