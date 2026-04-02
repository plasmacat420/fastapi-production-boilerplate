import pytest


@pytest.mark.asyncio
async def test_get_me(client, auth_headers, test_user):
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["user"].email


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    response = await client.get("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_me(client, auth_headers):
    response = await client.patch(
        "/users/me",
        headers=auth_headers,
        json={"full_name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_list_users_admin(client, admin_headers):
    response = await client.get("/users", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_users_forbidden(client, auth_headers):
    response = await client.get("/users", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_admin(client, admin_headers, test_user):
    user_id = str(test_user["user"].id)
    response = await client.delete(f"/users/{user_id}", headers=admin_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_user_forbidden(client, auth_headers, test_admin):
    admin_id = str(test_admin["user"].id)
    response = await client.delete(f"/users/{admin_id}", headers=auth_headers)
    assert response.status_code == 403
