#!/usr/bin/env python3
"""Seed the database with test users."""

import asyncio
import sys

sys.path.insert(0, ".")

from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import app.models  # noqa: E402, F401
from app.config import settings  # noqa: E402
from app.services.user import create_user, get_user_by_email  # noqa: E402


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    created = []

    async with session_factory() as db:
        # Create 10 regular users
        for i in range(1, 11):
            email = f"user{i:02d}@example.com"
            existing = await get_user_by_email(db, email)
            if existing:
                print(f"  skip {email} (already exists)")
                continue
            user = await create_user(
                db,
                email=email,
                password="password123",
                full_name=f"Test User {i:02d}",
                role="user",
            )
            created.append(user)

        # Create 1 moderator
        mod_email = "moderator@example.com"
        existing = await get_user_by_email(db, mod_email)
        if not existing:
            mod = await create_user(
                db,
                email=mod_email,
                password="modpass123",
                full_name="Moderator User",
                role="moderator",
            )
            created.append(mod)

        await db.commit()

    print(f"\nSeeded {len(created)} users:\n")
    print(f"{'Email':<35} {'Role':<12} {'Name'}")
    print("-" * 65)
    for u in created:
        print(f"{u.email:<35} {u.role:<12} {u.full_name}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
