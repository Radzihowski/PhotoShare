from src.database.enums import Role
from src.utils.py_logger import get_logger
from fastapi import  status, Security,  HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.services.auth import auth_service
from src.database.models import User
security = HTTPBearer()
logger = get_logger(__name__)
class RoleAccess:
    def __init__(self, allowed_role: Role):
        self.allowed_role = allowed_role

    async def __call__(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
        user = await auth_service.get_current_user(credentials.credentials)
        logger.info(f"Current role: {user.role}, expected role: {self.allowed_role}")
        if user.role != self.allowed_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role below access level")
        return user