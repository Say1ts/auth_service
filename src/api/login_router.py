

from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from auth.exceptions import incorrect_username_or_password
from auth.services import authenticate_user
from auth.services import get_new_tokens_for_user_by_refresh_token
from auth.services import create_pair_of_tokens
from auth.schemas import Token
from auth.schemas import RefreshToken
from session import get_async_db

login_router = APIRouter()


@login_router.post("/login", response_model=Token)
async def login_for_access_and_refresh_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise incorrect_username_or_password
    refresh_token, access_token = create_pair_of_tokens(user)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@login_router.post("/refresh", response_model=Token)
async def login_for_access_token(
        data: RefreshToken,
        db: AsyncSession = Depends(get_async_db),
):
    new_refresh_token, access_token = await get_new_tokens_for_user_by_refresh_token(data.refresh_token, db)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": new_refresh_token}
