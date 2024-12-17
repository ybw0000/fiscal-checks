from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.dependencies import get_db_session
from src.checks.service import CheckService


async def get_check_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> CheckService:
    """Dependency to get UserService instance"""
    return CheckService(session)
