import json
import logging
import uuid

import coloredlogs
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import crud, db_helper
from app.database.redis_date import RedisTools
from app.routers.publisher import produce_message
from app.schemas.schemas import CreatePackage, GetPackage, PackageBase, TypeOrder

router = APIRouter()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(
    level="INFO", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)


@router.get("/", tags=["session"])
async def get_session(
        response: Response,
        request: Request,
        session: AsyncSession = Depends(db_helper.session_dependency),  # noqa: B008
):
    session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = await crud.create_user(session)
        logger.info("generated session value: %s", session_id)
        response.set_cookie(key="session_id", value=str(session_id), expires=100000)
        return session_id
    logger.info("there is already a session: %s", session_id)
    return session_id


# def send_to_broker(package: CreatePackage):
#     produce_message(package=package)


@router.post("/", tags=["orders"])
async def create_order(request: Request,
                       order_in: PackageBase
                       ):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session ID is missing from cookies",
        )
    unic_id = uuid.uuid4()

    package = CreatePackage(
        **order_in.model_dump(),
        user_id=session_id,
        cost_shipping=0,
        unic_id=str(unic_id)
    )

    # send_message(package=package)
    produce_message(package=package)

    logger.info("sending data to the broker: %s", unic_id)
    return unic_id


@router.get("/types/", response_model=list[TypeOrder])
async def get_type(
        session: AsyncSession = Depends(db_helper.session_dependency),  # noqa: B008
):
    return await crud.get_type(session=session)


@router.post("/orders/{pagination}", tags=["orders"], response_model=list[GetPackage])
async def get_all_order(
        request: Request,
        type_package: int,
        cost_bool: bool,
        pages: int,
        page_size: int,
        session: AsyncSession = Depends(db_helper.session_dependency)  # noqa: B008
):
    session_id = request.cookies.get("session_id")
    if session_id:
        user = await crud.get_user(session=session, session_id=session_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="no user in database"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="session dont"
        )

    result = await crud.get_orders(
        session=session, filter_types=type_package, cost_bool=cost_bool, user_id=user.id
    )
    if result:
        return list(result)[((pages - 1) * page_size): (pages * page_size)]
    else:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="user does not have packages"
        )


@router.get("/orders/{order_id}/", tags=["orders"], response_model=GetPackage)
async def get_order_id(
        order_id: str,
        session: AsyncSession = Depends(db_helper.session_dependency),  # noqa: B008
) -> GetPackage | None:
    package_r = await RedisTools.get_value(order_id)
    if package_r:
        package = package_r.decode("utf-8")
        logger.info("data is taken from cache")

        package = json.loads(package)
        logger.info("package: s%", package)
        result = GetPackage(**package)

        return result
    else:
        package = await crud.get_order_id(session=session, order_id=order_id)
        if package:
            logger.info("data is taken from database")
            return package
        else:
            logger.info("order not found: s%", order_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order {order_id} not found!",
            )
