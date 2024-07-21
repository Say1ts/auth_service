from logging import getLogger

from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.services import get_current_user_from_token
from exceptions import handle_integrity_error, handle_not_found_error, handle_conflict_error, \
    handle_unprocessable_entity_error
from session import get_async_db
from user.schemas import DeleteUserResponse, ShowUser, UpdateUserRequest, UpdatedUserResponse, UserCreate, UserDTO
from user.services import _create_new_user, _delete_user, _update_user
from user.validations import validate_user_exists, validate_permissions, validate_superadmin, validate_self_modification

logger = getLogger(__name__)

user_router = APIRouter()


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_async_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        handle_integrity_error(logger, err)


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserDTO = Depends(get_current_user_from_token),
) -> ShowUser:
    user = await validate_user_exists(user_id, db)
    return ShowUser.model_validate(user)


@user_router.patch("/", response_model=UpdatedUserResponse)
async def update_user_by_id(
        user_id: int,
        body: UpdateUserRequest,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserDTO = Depends(get_current_user_from_token),
) -> UpdatedUserResponse:
    updated_user_params = body.dict(exclude_none=True)
    if not updated_user_params:
        handle_unprocessable_entity_error("At least one parameter for user update info should be provided")
    user_for_update = await validate_user_exists(user_id, db)
    if user_id != current_user.user_id:
        validate_permissions(user_for_update, current_user)
    try:
        updated_user_id = await _update_user(updated_user_params=updated_user_params, session=db, user_id=user_id)
    except IntegrityError as err:
        handle_integrity_error(logger, err)
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserDTO = Depends(get_current_user_from_token),
) -> DeleteUserResponse:
    user_for_deletion = await validate_user_exists(user_id, db)
    validate_permissions(user_for_deletion, current_user)
    deleted_user_id = await _delete_user(user_id, db)
    if deleted_user_id is None:
        handle_not_found_error("User", user_id)
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.patch("/admin_privilege", response_model=UpdatedUserResponse)
async def grant_admin_privilege(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserDTO = Depends(get_current_user_from_token),
):
    validate_superadmin(current_user)
    validate_self_modification(current_user.user_id, user_id)
    user_for_promotion = await validate_user_exists(user_id, db)
    if user_for_promotion.is_admin or user_for_promotion.is_superadmin:
        handle_conflict_error(f"User with id {user_id} already promoted to admin / superadmin.")
    try:
        user_for_promotion.enrich_admin_role_by_admin_role()
    except IntegrityError as err:
        handle_integrity_error(logger, err)
    return UpdatedUserResponse(updated_user_id=user_for_promotion)


@user_router.delete("/admin_privilege", response_model=UpdatedUserResponse)
async def revoke_admin_privilege(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: UserDTO = Depends(get_current_user_from_token),
):
    validate_superadmin(current_user)
    validate_self_modification(current_user.user_id, user_id)
    user_for_revoke_admin_privileges = await validate_user_exists(user_id, db)
    if not user_for_revoke_admin_privileges.is_admin:
        handle_conflict_error(f"User with id {user_id} has no admin privileges.")
    updated_user_params = {"roles": user_for_revoke_admin_privileges.remove_admin_privileges_from_model()}
    try:
        updated_user_id = await _update_user(updated_user_params=updated_user_params, session=db, user_id=user_id)
    except IntegrityError as err:
        handle_integrity_error(logger, err)
    return UpdatedUserResponse(updated_user_id=updated_user_id)
