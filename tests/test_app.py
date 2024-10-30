import uuid

import pytest
from sqlalchemy import insert, select
from httpx import AsyncClient

from pydantic import ValidationError
from app.database import UserModel
from app.schemas.schemas import CreatePackage
from tests import test_data
from tests.conftest import client, async_session_maker


async def test_add_user():
    async with async_session_maker() as session:
        stmt = insert(UserModel).values(id=1, user_id=1111)
        await session.execute(stmt)
        await session.commit()

        query = select(UserModel)
        result = await session.execute(query)

        users = result.scalars().all()
        assert [(user.id, user.user_id) for user in users] == [(2, 1111)], 'User dont add'     # noqa: 501


def test_get_session():
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.parametrize('data, res', test_data.create_order_data)
def test_validate_data_create_order(data, res):
    unic_id = uuid.uuid4()
    try:
        test_package = CreatePackage(
            **data,
            user_id="session123",
            cost_shipping=0,
            unic_id=str(unic_id)
        )
        assert test_package.package_name == data["package_name"]
        assert res == (test_package.weight == data["weight"])
        assert res == (test_package.type_id == data["type_id"])
        assert res == (test_package.cost_content == data["cost_content"])
        assert res is True

    except ValidationError:
        assert res is False


# @pytest.mark.parametrize('data, res', test_data.create_order_data)
# def test_create_order(mocker, data, res):
#     mocker.patch("app.routers.publisher.produce_message", None)
#
#     try:
#         unic_id = uuid.uuid4()
#         expected_package = CreatePackage(
#             **data,
#             user_id="session123",
#             cost_shipping=0,
#             unic_id=str(unic_id)
#         )
#         response = client.post(
#             "/",
#             json=data,
#             #cookies={"session_id": "session123"}
#         )
#         assert response.status_code == 200
#     except ValidationError:
#         assert res is False
#
#     unic_id = uuid.uuid4()
#     assert publisher.produce_message(expected_package) == 3


async def test_get_order_all(ac: AsyncClient):
    params = {
        "type_package": "0",
        "cost_bool": True,
    }
    response = await ac.post("/order_all/1/", json=params)
    assert response.status_code == 200


# def test_get_order_id():
#     client.get("/order/{order_id}/", json="")
#

def test_get_type():
    response = client.get("/types/")
    assert response.status_code == 200
