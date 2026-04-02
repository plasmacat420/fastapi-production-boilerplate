#!/usr/bin/env python3
"""CLI script to create the first admin user."""

import asyncio
import sys

import click
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Allow running from project root
sys.path.insert(0, ".")

import app.models  # noqa: E402, F401
from app.config import settings  # noqa: E402
from app.services.user import create_user, get_user_by_email  # noqa: E402


async def _create_admin(email: str, password: str, name: str) -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as db:
        existing = await get_user_by_email(db, email)
        if existing:
            click.echo(
                f"[!] User with email '{email}' already exists (role={existing.role})"
            )
            return

        user = await create_user(
            db, email=email, password=password, full_name=name, role="admin"
        )
        await db.commit()

    click.echo("[+] Admin user created successfully")
    click.echo(f"    ID:    {user.id}")
    click.echo(f"    Email: {user.email}")
    click.echo(f"    Name:  {user.full_name}")
    click.echo(f"    Role:  {user.role}")

    await engine.dispose()


@click.command()
@click.option("--email", required=True, help="Admin email address")
@click.option("--password", required=True, help="Admin password (min 8 chars)")
@click.option("--name", default="Admin User", show_default=True, help="Full name")
def create_admin(email: str, password: str, name: str) -> None:
    """Create an admin user in the database."""
    if len(password) < 8:
        click.echo("[!] Password must be at least 8 characters", err=True)
        sys.exit(1)
    asyncio.run(_create_admin(email, password, name))


if __name__ == "__main__":
    create_admin()
