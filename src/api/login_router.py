from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException, status
from fastapi import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import RefreshToken
from auth.schemas import Token
from auth.services import authenticate_user, get_current_user_from_token
from auth.services import create_pair_of_tokens
from auth.services import get_new_tokens_for_user_by_refresh_token
from auth.utils.security import OAuth2PasswordBearerWithCookie
from session import get_async_db
from user.schemas import UserDTO

login_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


@login_router.post("/login", response_model=Token)
async def login_for_access_and_refresh_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    refresh_token, access_token = create_pair_of_tokens(user)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}",
                        httponly=True)  # Устанавливаем HttpOnly cookie
    response.set_cookie(key="refresh_token", value=f"Bearer {refresh_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@login_router.post("/refresh", response_model=Token)
async def login_for_access_token(
        response: Response,
        data: RefreshToken,
        db: AsyncSession = Depends(get_async_db),
):
    new_refresh_token, access_token = await get_new_tokens_for_user_by_refresh_token(data.refresh_token, db)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}",
                        httponly=True)  # Устанавливаем HttpOnly cookie
    response.set_cookie(key="refresh_token", value=f"Bearer {new_refresh_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": new_refresh_token}


@login_router.get("/protected-route")
async def protected_route(
        current_user: Annotated[UserDTO, Depends(get_current_user_from_token)],
):
    return {}
