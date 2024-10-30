import logging

import coloredlogs
import pika

from app.schemas.schemas import CreatePackage

QUEUE_NAME = "package_queue"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(
    level="DEBUG", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)


def get_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))


def produce_message(package: CreatePackage) -> None:

    with get_connection() as connection:
        with connection.channel() as channel:
            channel.queue_declare(queue=QUEUE_NAME)
            logger.info("Broker has opened a channel: s%", QUEUE_NAME)

            package_json = package.model_dump(mode="json")
            channel.basic_publish(
                exchange="", routing_key=QUEUE_NAME, body=str(package_json)
            )
            logger.info("message has been sent: s%", package_json)
            connection.close()
