import logging

from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials
from starlette import status

from src.users.dependencies import auth_scheme
from src.users.dependencies import get_authenticated_user
from src.users.dependencies import get_user_service
from src.users.models import User
from src.users.schemas import JWTResponseSchema
from src.users.schemas import UserDTOCreateSchema
from src.users.schemas import UserDTOReadSchema
from src.users.schemas import UserDTOSignInSchema
from src.users.schemas import UserInfoUpdateDTOSchema
from src.users.service import UserService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users")


@router.get(
    "/me",
    responses={
        status.HTTP_200_OK: {"model": UserDTOReadSchema},
        status.HTTP_404_NOT_FOUND: {"model": None},
    },
)
async def me(user: Annotated[User, Depends(get_authenticated_user)]):
    return UserDTOReadSchema.model_validate(user)


@router.get(
    "/refresh",
    responses={
        status.HTTP_200_OK: {"model": JWTResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": None},
    },
)
async def refresh_token(
    token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    access_token, refresh_token = await service.refresh_access_token(token.credentials)
    return JWTResponseSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/signup",
    response_model=JWTResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"model": JWTResponseSchema},
        status.HTTP_409_CONFLICT: {"model": None},
    },
)
async def signup(
    request_data: UserDTOCreateSchema,
    service: Annotated[UserService, Depends(get_user_service)],
):
    access_token, refresh_token = await service.create_user(request_data)
    return JWTResponseSchema(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/signin",
    response_model=JWTResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": JWTResponseSchema},
    },
)
async def signin(
    request_data: UserDTOSignInSchema,
    service: Annotated[UserService, Depends(get_user_service)],
):
    access_token, refresh_token = await service.signin(request_data)
    return JWTResponseSchema(access_token=access_token, refresh_token=refresh_token)


@router.patch(
    "/update",
    responses={status.HTTP_200_OK: {"model": None}},
)
async def update(
    user: Annotated[User, Depends(get_authenticated_user)],
    request_data: UserInfoUpdateDTOSchema,
    service: Annotated[UserService, Depends(get_user_service)],
):
    await service.update(user, request_data.model_dump(mode="json", exclude_none=True, exclude_unset=True))
    return 200
