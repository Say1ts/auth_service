# validations.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from user.schemas import UserDTO
from user.services import _get_user_by_id, has_permissions_to_effect_the_target

async def validate_user_exists(user_id: int, db: AsyncSession):
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    return user

def validate_permissions(target_user: UserDTO, acting_user: UserDTO):
    if not has_permissions_to_effect_the_target(target_user=target_user, acting_user=acting_user):
        raise HTTPException(status_code=403, detail="Forbidden.")

def validate_superadmin(user: UserDTO):
    if not user.is_superadmin:
        raise HTTPException(status_code=403, detail="Forbidden.")

def validate_self_modification(current_user_id: int, target_user_id: int):
    if current_user_id == target_user_id:
        raise HTTPException(status_code=400, detail="Cannot manage privileges of itself.")
