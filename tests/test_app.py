from uuid import uuid4, UUID

import pytest
from sqlalchemy import insert, select

from pydantic import ValidationError
from app.database import UserModel
from app.schemas.schemas import CreatePackage
from tests import test_data
from tests.conftest import client, async_session_maker


@pytest.mark.asyncio()
async def test_add_user():
    async with async_session_maker() as session:
        stmt = insert(UserModel).values(id=1, user_id="c303282d-f2e6-46ca-a04a-35d3d873712d")   # noqa: 501
        await session.execute(stmt)
        await session.commit()

        query = select(UserModel)
        result = await session.execute(query)

        users = result.scalars().all()
        assert [(user.id, user.user_id) for user in users] == [
            (1, UUID("c303282d-f2e6-46ca-a04a-35d3d873712d"))], 'User dont add'  # noqa: 501


@pytest.mark.asyncio()
async def test_get_session_no_cookie(mocker, override_get_async_session):
    mocker.patch("app.database.crud.create_user", return_value="new_session_id")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "new_session_id"
    assert response.cookies.get("session_id") == "new_session_id"


@pytest.mark.parametrize('data, res', test_data.create_order_data)
def test_validate_data_create_order(data, res):
    unic_id = uuid4()
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


@pytest.mark.asyncio()
async def test_get_order_all(mocker):
    session_id = "1303282d-f2e6-46ca-a04a-35d3d873712d"

    user = {
        "id": "1",
        "user_id": "1234",
        "created_at": "2024-10-31 12:45:23.123456+00:00",
        "updated_at": None
    }

    mocker.patch("app.database.crud.get_user", return_value=UserModel(**user))
    mocker.patch("app.database.crud.get_orders", return_value=[test_data.mock_get_orders])  # noqa: 501

    response = client.post(
        "/orders/1",
        cookies={"session_id": session_id},
        params={
            "type_package": 0,
            "cost_bool": False,
            "pages": 1,
            "page_size": 10
        }
    )

    assert response.status_code == 200
    assert response.json() == [package.model_dump() for package in test_data.mock_get_orders]   # noqa: 501


def test_get_type():
    response = client.get("/types/")
    assert response.status_code == 200
