from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.database import Base
from app.database import db_helper
from app.database.setup_data import setup_execute
from app.routers.routers import router


@asynccontextmanager
async def lifespan(apps: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await setup_execute(conn)
    yield
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.commit()


app = FastAPI(title="MyShipping.com", lifespan=lifespan)


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
