import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "newpass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user):
    response = await client.post(
        "/auth/register",
        json={"email": test_user["user"].email, "password": "somepass123"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client):
    response = await client.post(
        "/auth/register",
        json={"email": "weak@example.com", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    response = await client.post(
        "/auth/login",
        json={"email": test_user["user"].email, "password": test_user["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    response = await client.post(
        "/auth/login",
        json={"email": test_user["user"].email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(client, test_user, db):
    from sqlalchemy import update

    from app.models.user import User

    await db.execute(
        update(User).where(User.id == test_user["user"].id).values(is_active=False)
    )
    await db.commit()

    response = await client.post(
        "/auth/login",
        json={"email": test_user["user"].email, "password": test_user["password"]},
    )
    assert response.status_code == 403

    # restore
    await db.execute(
        update(User).where(User.id == test_user["user"].id).values(is_active=True)
    )
    await db.commit()


@pytest.mark.asyncio
async def test_refresh_token(client, test_user):
    login = await client.post(
        "/auth/login",
        json={"email": test_user["user"].email, "password": test_user["password"]},
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_refresh_invalid_token(client):
    response = await client.post(
        "/auth/refresh", json={"refresh_token": "garbage.token.here"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client, auth_headers):
    response = await client.post("/auth/logout", headers=auth_headers)
    assert response.status_code == 200
