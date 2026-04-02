from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth import hash_password


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    role: str = "user",
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: UUID, data: dict) -> Optional[User]:
    await db.execute(update(User).where(User.id == user_id).values(**data))
    await db.flush()
    return await get_user_by_id(db, user_id)


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    await db.execute(update(User).where(User.id == user_id).values(is_active=False))
    await db.flush()
    return True


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 20) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_last_login(db: AsyncSession, user_id: UUID) -> None:
    from datetime import datetime, timezone

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(last_login=datetime.now(timezone.utc))
    )
    await db.flush()
