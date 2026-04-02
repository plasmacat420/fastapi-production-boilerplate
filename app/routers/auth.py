from fastapi import APIRouter, Depends, status

from app.database import get_db
from app.dependencies import get_current_active_user
from app.exceptions import AuthException, ConflictException, ForbiddenException
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import create_token_pair, verify_password, verify_token
from app.services.user import (
    create_user,
    get_user_by_email,
    update_last_login,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(payload: UserCreate, db=Depends(get_db)):
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise ConflictException("Email already registered")

    user = await create_user(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )
    return create_token_pair(str(user.id), user.role)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db=Depends(get_db)):
    user = await get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise AuthException("Invalid email or password")

    if not user.is_active:
        raise ForbiddenException("Account is deactivated")

    await update_last_login(db, user.id)
    return create_token_pair(str(user.id), user.role)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest):
    token_data = verify_token(payload.refresh_token, expected_type="refresh")
    user_id = token_data.get("sub")
    role = token_data.get("role", "user")
    if not user_id:
        raise AuthException("Invalid refresh token")
    return create_token_pair(user_id, role)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user=Depends(get_current_active_user)):
    # In a production system, blacklist the token's JTI in Redis with TTL
    # For this boilerplate we return 200 — clients must discard the token
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_active_user)):
    return current_user
