from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dependencies import get_db_session
from src.users.service import UserService


auth_scheme = HTTPBearer()


async def get_user_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> UserService:
    """Dependency to get UserService instance"""
    return UserService(session)


async def get_authenticated_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """Dependency to validate the Bearer token and return the authenticated user."""
    try:
        user = await user_service.verify_jwt_access_token(token.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token validation failed") from e
