import logging
from typing import List

import coloredlogs
from sqlalchemy import join, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.database import PackageModel, TypeModel, UserModel
from app.schemas.schemas import GetPackage

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(
    level="INFO", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)


async def create_user(session: AsyncSession):
    new_user = UserModel()
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user.user_id


async def get_user(session: AsyncSession, session_id: str):
    user = await session.scalar(
        select(UserModel).where(UserModel.user_id == session_id)
    )
    return user


async def get_type(session: AsyncSession):
    types = await session.scalars(select(TypeModel))
    return types.all()


async def get_orders(
    session: AsyncSession, filter_types: int, cost_bool: bool, user_id: str
) -> List[GetPackage]:
    stmt = (
        select(
            PackageModel.package_name,
            PackageModel.unic_id,
            PackageModel.weight,
            PackageModel.cost_content,
            PackageModel.cost_shipping,
            TypeModel.type_name,
            PackageModel.created_at,
            PackageModel.updated_at,
        )
        .select_from(
            join(PackageModel, TypeModel, PackageModel.type_id == TypeModel.id)
        )
        .where(PackageModel.user_id == user_id)
    )

    if cost_bool:
        stmt = stmt.where(PackageModel.cost_shipping.isnot(None))

    if filter_types > 0:
        stmt = stmt.where(PackageModel.type_id == filter_types)

    result = await session.execute(stmt)
    return result.all()


async def get_order_id(session: AsyncSession, order_id: str) -> GetPackage | None:
    p = aliased(PackageModel)
    t = aliased(TypeModel)
    stmt = (
        select(
            p.package_name,
            p.unic_id,
            p.weight,
            p.cost_content,
            p.cost_shipping,
            t.type_name,
        )
        .join(t, p.type_id == t.id)
        .where(p.unic_id == str(order_id))
    )

    result = await session.execute(stmt)
    return result.first()
