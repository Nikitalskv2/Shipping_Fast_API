from fastapi import Depends
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import TypeModel, db_helper


async def setup_execute(
    session: AsyncSession = Depends(db_helper.session_dependency),  # noqa: B008
):
    types = insert(TypeModel).values(
        [
            {"type_name": "clothing"},
            {"type_name": "electronics"},
            {"type_name": "other"},
        ]
    )
    await session.execute(types)
    await session.commit()
