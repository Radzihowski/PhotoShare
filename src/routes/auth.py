from fastapi import APIRouter, HTTPException, status, Security, BackgroundTasks, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_limiter.depends import RateLimiter

from src.repository import users as repository_users
from src.schemas.users import UserModel, UserResponse, TokenModel
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request):
    exist_user = await repository_users.get_user_by_email(body.email)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body)
    background_tasks.add_task(send_email, new_user["email"], "mate", str(request.base_url))
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def login(body: UserModel):
    user = await repository_users.get_user_by_email(body.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel, dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email)
    if user.refresh_token != token:
        await repository_users.update_token(user, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}', status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def confirmed_email(token: str):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email)
    return {"message": "Email confirmed"}

@router.get('/logout', status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def logout(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    auth_service.add_token_to_blacklist(token)
    return {"message": "Successfully logged out"}