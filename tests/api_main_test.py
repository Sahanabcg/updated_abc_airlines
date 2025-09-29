import pytest


@pytest.mark.asyncio
async def test_status_by_ticket_owner_only(client, as_a, seed_data):
    t_a = seed_data["t_a"]
    r = await client.get(f"/api/v1/main_api/status_by_ticket/{t_a.id}")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) >= 1


@pytest.mark.asyncio
async def test_status_by_ticket_other_forbidden(client, as_b, seed_data):
    t_a = seed_data["t_a"]
    r = await client.get(f"/api/v1/main_api/status_by_ticket/{t_a.id}")
    assert r.status_code in (403, 404)


@pytest.mark.asyncio
async def test_customer_lookup_owner(client, as_a, seed_data):
    ev1 = seed_data["ev1"]
    r = await client.get(f"/api/v1/main_api/customer_lookup/{ev1.id}")
    assert r.status_code == 200
    data = r.json()
    assert "email" in data and "hashed_pasword" not in data


@pytest.mark.asyncio
async def test_customer_lookup_other_forbidden(client, as_b, seed_data):
    ev1 = seed_data["ev1"]
    r = await client.get(f"/api/v1/main_api/customer_lookup/{ev1.id}")
    assert r.status_code in (403, 404)


@pytest.mark.asyncio
async def test_customer_lookup_admin_ok(client, as_admin, seed_data):
    ev1 = seed_data["ev1"]
    r = await client.get(f"/api/v1/main_api/customer_lookup/{ev1.id}")
    assert r.status_code == 200
