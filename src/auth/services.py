from datetime import timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from session import get_async_db
from user.dals import SQLAlchemyUserDAL as UserDAL
from user.schemas import UserDTO
from .exceptions import credentials_exception, cannot_create_refresh_token, cannot_create_access_token, user_is_none
from .utils.hashing import Hasher
from .utils.security import create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def _get_user_by_email_for_auth(email: str, session: AsyncSession):
    async with session.begin():
        user_dal = UserDAL(session)
        return await user_dal.get_user_by_email(
            email=email,
        )


async def authenticate_user(
        email: str, password: str, db: AsyncSession
) -> Optional[UserDTO]:
    user = await _get_user_by_email_for_auth(email=email, session=db)
    if user is None:
        return
    if not Hasher.verify_password(password, user.hashed_password):
        return
    return user


async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)
) -> UserDTO:
    try:
        payload = jwt.decode(
            token, settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM]
        )
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await _get_user_by_email_for_auth(email=email, session=db)
    if user is None:
        raise credentials_exception
    return UserDTO.model_validate(user)


def create_pair_of_tokens(user: UserDTO) -> (str, str):
    """
    Create new token pair: access and refresh tokens.
    """
    if not user:
        raise Exception('User is None')
    try:
        refresh_token_expires = timedelta(minutes=settings.AUTH_REFRESH_TOKEN_EXPIRE_WEEKS)
        refresh_token = create_access_token(
            data={
                "user_id": user.user_id,
                "email": user.email,
            },

            expires_delta=refresh_token_expires,
        )
    except JWTError:
        raise cannot_create_refresh_token

    try:
        access_token_expires = timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "user_id": user.user_id,
                "name": user.name,
                "surname": user.surname,
                "email": user.email,
                "role": user.role,
                "refresh_expires": refresh_token_expires,
            },

            expires_delta=access_token_expires,
        )
    except JWTError:
        raise cannot_create_access_token

    return refresh_token, access_token


async def check_refresh_token_and_get_user(
        token: str, db: AsyncSession = Depends(get_async_db)
) -> UserDTO:

    try:
        payload = jwt.decode(
            token, settings.AUTH_SECRET_KEY, algorithms=[settings.AUTH_ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise user_is_none
        user_dal = UserDAL(db)
        user = await user_dal.get_user_by_id(user_id=user_id)
        if not user:
            raise user_is_none

        return user

    except JWTError:
        raise credentials_exception


async def get_new_tokens_for_user_by_refresh_token(
        token: str
):
    user = await check_refresh_token_and_get_user(token)
    refresh_token, access_token = create_pair_of_tokens(user)
    return refresh_token, access_token

