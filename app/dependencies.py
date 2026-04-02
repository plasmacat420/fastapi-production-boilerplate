from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.database import get_db
from app.exceptions import AuthException, ForbiddenException
from app.models.user import User
from app.services.auth import verify_token
from app.services.user import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
) -> User:
    payload = verify_token(token, expected_type="access")
    user_id = payload.get("sub")
    if not user_id:
        raise AuthException("Invalid token payload")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise AuthException("User not found")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise ForbiddenException("Account is deactivated")
    return current_user


def require_role(*roles: str):
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"Role '{current_user.role}' is not allowed. Required: {list(roles)}"
            )
        return current_user

    return role_checker
