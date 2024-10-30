import logging

import coloredlogs
import httpx
from pydantic import BaseModel, ValidationError
from redis import asyncio as ioredis

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
coloredlogs.install(
    level="INFO", logger=logger, fmt="%(asctime)s - %(levelname)s - %(message)s"
)


CBR_url = "https://www.cbr-xml-daily.ru/daily_json.js"
REDIS_KEY_USD = "usd-rub"


class Currency(BaseModel):
    ID: str
    NumCode: int
    CharCode: str
    Nominal: int
    Name: str
    Value: float
    Previous: float


class Currencies(BaseModel):
    Valute: dict[str, Currency]


class RedisTools:
    redis_connect = ioredis.Redis(host="localhost", encoding="utf-8")

    @classmethod
    async def fetch_usd_to_rub(cls):
        timeout = httpx.Timeout(timeout=10)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(CBR_url)
            data = response.json()
            try:
                currencies = Currencies(**data)
                usd_rate = currencies.Valute["USD"].Value
                logger.info("get currency usd-rub: s%", usd_rate)
                return usd_rate
            except ValidationError as e:
                logger.error("Ошибка валидации данных: %s", e)
                raise

    @classmethod
    async def update_usd_to_rub(cls):
        usd_rate = await cls.fetch_usd_to_rub()
        await cls.redis_connect.set(REDIS_KEY_USD, usd_rate, ex=86400)
        logger.info("currency update: s%", usd_rate)

    @classmethod
    async def get_usd_to_rub(cls):
        usd_rate = await cls.redis_connect.get(REDIS_KEY_USD)
        if usd_rate:
            return usd_rate
        else:
            await cls.update_usd_to_rub()
            return await cls.get_usd_to_rub()

    @classmethod
    async def set_order(cls, order_id, value):
        await cls.redis_connect.set(order_id, value, ex=60 * 60)
        logger.info("write order to cache")

    @classmethod
    async def get_order(cls, order_id):
        value = await cls.redis_connect.get(order_id)
        if value:
            logger.info("read order to cache")

            return value
