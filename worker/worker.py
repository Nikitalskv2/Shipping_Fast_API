import asyncio
import json
import logging
from typing import TYPE_CHECKING

import coloredlogs
import pika
from database_worker import async_session
from model_worker import PackageModel, TypeModel, UserModel
from redis_date import RedisTools
from schemas_worker import CreatePackage, GetPackage
from sqlalchemy import select
from sqlalchemy.orm import aliased

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(
    level="INFO", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)

QUEUE_NAME = "package_queue"


if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


def receiver(
    ch: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
):
    logger.info("message has arrived, started loop")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_message(ch, body))


async def process_message(ch, body: bytes):

    body_str = body.decode("utf-8")
    new_body = body_str.replace("'", '"')
    package = json.loads(new_body)

    logger.info("message: s%", new_body)
    logger.info("package: s%", package)
    order_in = CreatePackage(**package)
    await create_order(order_in=order_in)


async def create_order(order_in: CreatePackage):

    redis_rate = await RedisTools.get_usd_to_rub()
    rate = float(redis_rate)
    logger.info("get usd-rub: s%", rate)

    order_in.cost_shipping = round(
        (order_in.weight * 0.5 + order_in.cost_content * 0.01) * rate, 2
    )
    order_in.user_id = await get_user(str(order_in.user_id))
    logger.info(
        "calculate the shipping cost, get the user id: cost: s%, user: s%",
        order_in.cost_shipping,
        order_in.user_id,
    )

    package = PackageModel(**order_in.model_dump())

    async with async_session() as session:
        session.add(package)
        await session.commit()
        logger.info("order message has been added to database")

    result = await get_order_id(order_in.unic_id)
    if result:
        data = {
            "package_name": result.package_name,
            "unic_id": result.unic_id,
            "weight": result.weight,
            "cost_content": result.cost_content,
            "cost_shipping": result.cost_shipping,
            "type_name": result.type_name,
            "created_at": str(result.created_at),
            "updated_at": result.updated_at,
        }

        json_string = json.dumps(data)
        await RedisTools.set_order(order_in.unic_id, json_string)
    else:
        logger.error("Order not found for ID: %s", order_in.unic_id)


async def get_order_id(order_id: str) -> GetPackage | None:

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
            p.created_at,
            p.updated_at,
        )
        .join(t, p.type_id == t.id)
        .where(p.unic_id == str(order_id))
    )

    async with async_session() as session:
        result = await session.execute(stmt)
        return result.fetchone()


async def get_user(user_id: str) -> int:
    async with async_session() as session:
        user = await session.scalar(
            select(UserModel).where(UserModel.user_id == str(user_id))
        )
        logger.info("get user id from db: s%", user.id)
        return user.id


def get_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(pika.ConnectionParameters())


def start_worker():
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=receiver, auto_ack=True)
    logger.info("Worker is waiting for messages")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        start_worker()
    except KeyboardInterrupt:
        logger.info("Interrupted")
