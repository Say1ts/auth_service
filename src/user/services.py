from typing import Optional

from fastapi import HTTPException

from auth import Hasher

from .dals import SQLAlchemyUserDAL as UserDAL
from .schemas import UserRole, UserDTO
from .schemas import ShowUser
from .schemas import UserCreate


async def _create_new_user(body: UserCreate, session) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            username=body.username,
            # name=body.name,
            # surname=body.surname,
            email=body.email,
            hashed_password=Hasher.get_password_hash(body.password),
            role=UserRole.ROLE_USER,
        )
        return ShowUser(
            username=user.username,
            user_id=user.user_id,
            # name=user.name,
            # surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def _delete_user(user_id, session) -> Optional[int]:
    async with session.begin():
        user_dal = UserDAL(session)
        deleted_user_id = await user_dal.delete_user(
            user_id=user_id,
        )
        return deleted_user_id


async def _update_user(
        updated_user_params: dict, user_id: int, session
) -> Optional[int]:
    async with session.begin():
        user_dal = UserDAL(session)
        updated_user_id = await user_dal.update_user(
            user_id=user_id, **updated_user_params
        )
        return updated_user_id


async def _get_user_by_id(user_id, session) -> Optional[UserDTO]:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(
            user_id=user_id,
        )
        if user is not None:
            return user


def has_permissions_to_effect_the_target(target_user: UserDTO, acting_user: UserDTO) -> bool:
    if target_user.role == UserRole.ROLE_SUPERADMIN:
        raise HTTPException(
            status_code=406, detail="Superadmin cannot be deleted via API."
        )
    if target_user.user_id == acting_user.user_id:
        return False
    # check admin role
    if not acting_user.is_superadmin or not acting_user.is_admin:
        return False
    # check admin deactivate admin attempt
    if target_user.is_admin and acting_user.is_admin:
        return False
    return True
