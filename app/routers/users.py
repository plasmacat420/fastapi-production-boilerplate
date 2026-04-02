from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.database import get_db
from app.dependencies import get_current_active_user, require_role
from app.exceptions import ForbiddenException, NotFoundException
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import delete_user, get_user_by_id, list_users, update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user=Depends(get_current_active_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    payload: UserUpdate,
    current_user=Depends(get_current_active_user),
    db=Depends(get_db),
):
    updated = await update_user(
        db, current_user.id, payload.model_dump(exclude_none=True)
    )
    return updated


@router.get("", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _admin=Depends(require_role("admin")),
    db=Depends(get_db),
):
    return await list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user=Depends(get_current_active_user),
    db=Depends(get_db),
):
    if current_user.role != "admin" and str(current_user.id) != str(user_id):
        raise ForbiddenException("Cannot access another user's profile")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: UUID,
    _admin=Depends(require_role("admin")),
    db=Depends(get_db),
):
    deleted = await delete_user(db, user_id)
    if not deleted:
        raise NotFoundException("User not found")
