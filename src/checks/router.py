import logging

from typing import Annotated

from fastapi import APIRouter
from fastapi import Request
from fastapi.params import Depends
from fastapi.params import Query
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.checks.dependencies import get_check_service
from src.checks.schemas import CheckDTOCreateSchema
from src.checks.schemas import CheckDTOResponseSchema
from src.checks.schemas import ChecksWithPaginationResponseSchema
from src.checks.schemas import FilterParams
from src.checks.service import CheckService
from src.checks.service import MarkupService
from src.users.dependencies import get_authenticated_user
from src.users.models import User


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/checks")

templates = Jinja2Templates(directory="src/checks/templates")


@router.get(
    "/",
    responses={
        200: {"model": ChecksWithPaginationResponseSchema},
    },
)
async def checks_list(
    user: Annotated[User, Depends(get_authenticated_user)],
    service: Annotated[CheckService, Depends(get_check_service)],
    query_params: Annotated[FilterParams, Query()],
):
    return await service.get_user_checks(user, query_params)


@router.get("/{id}", response_class=HTMLResponse)
async def check_detail(request: Request, id: int, service: Annotated[CheckService, Depends(get_check_service)]):
    return templates.TemplateResponse(
        request,
        name="check.html",
        context={
            "data": MarkupService(await service.get_check(id)).build_markup(),
        },
    )


@router.post(
    "/create",
    responses={
        201: {"model": CheckDTOResponseSchema},
    },
)
async def create_check(
    user: Annotated[User, Depends(get_authenticated_user)],
    request_data: CheckDTOCreateSchema,
    service: Annotated[CheckService, Depends(get_check_service)],
):
    check = await service.create_check(user, request_data)
    return CheckDTOResponseSchema.model_validate(check)
