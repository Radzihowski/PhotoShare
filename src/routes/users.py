from fastapi import APIRouter, Depends, status, UploadFile, File, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas.users import UserDb


router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()

@router.get("/me/", response_model=UserDb)
async def read_users_me(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    return user

@router.patch('/avatar', status_code=status.HTTP_200_OK)
async def update_avatar_user(file: UploadFile = File(), credentials: HTTPAuthorizationCredentials = Security(security)):
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )
    token = credentials.credentials
    current_user = await auth_service.get_current_user(token)
    public_id = f'PhotoShare/{current_user.id}/avatar'
    r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    src_url = cloudinary.CloudinaryImage(r['public_id']).build_url(
        width=250, height=250, crop='fill',
        version=r['version'], format=r['format'], secure=True
    )
    await repository_users.update_avatar(current_user.email, src_url)
    return {"url": src_url, "detail": "Avatar successfully updated"}
