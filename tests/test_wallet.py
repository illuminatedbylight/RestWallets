import pytest
import asyncio
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_wallet_lifecycle(client: AsyncClient):

    response = await client.post("/api/v1/wallets")
    assert response.status_code == 200
    wallet_data = response.json()
    wallet_id = wallet_data["wallet_id"]
    assert wallet_data["balance"] == "0.00"

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 157.15},
    )
    assert response.status_code == 200
    wallet_data = response.json()
    assert wallet_data["status"] == "success"
    assert wallet_data["wallet_id"] == wallet_id
    assert wallet_data["balance"] == "157.15"

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 52.32},
    )
    assert response.status_code == 200
    wallet_data = response.json()
    assert wallet_data["status"] == "success"
    assert wallet_data["wallet_id"] == wallet_id
    assert wallet_data["balance"] == "104.83"

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 200.00},
    )
    assert response.status_code == 400
    error_data = response.json()
    assert error_data["detail"] == "Insufficient funds"

    response = await client.post(
        f"/api/v1/wallets/{uuid4()}/operation",
        json={"operation_type": "WITHDRAW", "amount": 104.83},
    )
    assert response.status_code == 404
    error_data = response.json()
    assert error_data["detail"] == "Wallet not found"

    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 200
    wallet_data = response.json()
    assert wallet_data["wallet_id"] == wallet_id
    assert wallet_data["balance"] == "104.83"

    response = await client.get(f"/api/v1/wallets/{uuid4()}")
    assert response.status_code == 404
    error_data = response.json()
    assert error_data["detail"] == "Wallet not found"


@pytest.mark.asyncio
async def test_concurrent_withdrawals(client: AsyncClient):
    response = await client.post("/api/v1/wallets")
    wallet_id = response.json()["wallet_id"]

    await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 100.00},
    )

    async def withdraw():
        return await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": 10.00},
        )

    tasks = [withdraw() for _ in range(10)]
    results = await asyncio.gather(*tasks)

    success_count = sum(1 for r in results if r.status_code == 200)
    fail_count = sum(1 for r in results if r.status_code == 400)

    assert success_count == 10
    assert fail_count == 0

    final_balance = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert final_balance.json()["balance"] == "0.00"
