from redis import asyncio as ioredis


class RedisTools:
    redis_connect = ioredis.Redis(host="localhost", encoding="utf-8")

    @classmethod
    async def get_value(cls, key):
        value = await cls.redis_connect.get(key)
        if value:
            return value
