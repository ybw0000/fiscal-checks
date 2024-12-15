from datetime import UTC
from datetime import datetime
from datetime import timedelta

import jwt

from src.base.service import BaseService
from src.conf.exceptions import AlreadyExistsException
from src.conf.exceptions import DoesNotExistException
from src.conf.settings import settings
from src.users.auth import Hasher
from src.users.models import User
from src.users.schemas import UserDTOCreateSchema
from src.users.schemas import UserDTOSignInSchema


class UserService(BaseService):
    MODEL = User

    async def get_user(self, pk: int = None, username: str = None) -> User | None:
        """Get user by his primary key or username."""
        assert pk or username, 'One of "pk" or "username" must be provided'
        filters = ()
        if pk:
            filters += (self.MODEL.id == pk,)
        if username:
            filters += (self.MODEL.username == username,)
        user = await self.fetch_one(filters)
        if not user:
            raise DoesNotExistException("User with provided data not found")
        return user

    async def create_user(self, request_data: UserDTOCreateSchema) -> tuple[str, str]:
        """Create a new user."""
        user = await self.fetch_one(filters=((self.MODEL.username == request_data.username),))
        if user:
            raise AlreadyExistsException('User with username "%s" already exists' % request_data.username)
        user = await self.insert(request_data.get_data_to_create())
        return await self.generate_jwt_tokens(user)

    async def signin(self, request_data: UserDTOSignInSchema) -> tuple[str, str]:
        """Sign in user."""
        user: User = await self.fetch_one(filters=(self.MODEL.username == request_data.username,))
        if not user or Hasher.hash_password(request_data.password) != user.password:
            raise DoesNotExistException("User with provided data not found")
        return await self.generate_jwt_tokens(user)

    async def generate_jwt_tokens(self, user: User) -> tuple[str, str]:
        """Get JWT token for user."""
        access_payload = {"iss": user.id, "exp": (datetime.now(UTC) + timedelta(minutes=5))}
        refresh_payload = {"iss": user.id, "exp": (datetime.now(UTC) + timedelta(hours=1))}
        access_token = jwt.encode(access_payload, user.password, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")
        return access_token, refresh_token

    async def verify_jwt_access_token(self, token: str) -> bool | User:
        """Verify the validity of a JWT token."""
        try:
            raw_data = jwt.decode(token, algorithms=["HS256"], options={"verify_signature": False})
            user = await self.get_user(raw_data["iss"])
            jwt.decode(token, user.password, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
            return False
        return user

    async def verify_jwt_refresh_token(self, token: str) -> bool:
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, KeyError):
            return False
        return True

    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        valid_refresh = await self.verify_jwt_refresh_token(refresh_token)
        if not valid_refresh:
            raise DoesNotExistException("Invalid or expired refresh token.")
        raw_data = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        user = await self.get_user(raw_data["iss"])
        if not user:
            raise DoesNotExistException("User not found for the provided refresh token.")
        return await self.generate_jwt_tokens(user)
