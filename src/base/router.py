import logging

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.base.dependencies import get_db_session
from src.base.schemas import PingResponseSchema


router = APIRouter(prefix="/base")

logger = logging.getLogger(__name__)


@router.get("/ping", responses={status.HTTP_200_OK: {"model": PingResponseSchema}})
async def ping(db_session: Annotated["AsyncSession", Depends(get_db_session)]) -> PingResponseSchema:
    await db_session.execute(select(1))
    return PingResponseSchema(OK=db_session.is_active)
