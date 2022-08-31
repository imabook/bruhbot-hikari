import asyncio
import aiomysql


class Database():

    def __init__(self, pool):
        self.__pool = pool

    async def close(self):
        self.__pool.close()
        await self.__pool.wait_closed()

    async def execute(self, *args, **kwargs):
        """Wrapper for single execute call"""
        async with self.__pool.acquire() as conn:
            c = await conn.cursor()
            response = await c.execute(*args, **kwargs)
            await conn.commit()

            return response

    async def fetch(self, *args, **kwargs):
        """Wrapper for single fetch call"""
        async with self.__pool.acquire() as conn:
            c = await conn.cursor()
            await c.execute(*args, **kwargs)

            return await c.fetchall()

    async def fetchone(self, *args, **kwargs):
        """Wrapper for single fetchone call"""
        async with self.__pool.acquire() as conn:
            c = await conn.cursor()
            await c.execute(*args, **kwargs)

            d = await c.fetchone()

            if d and len(d) == 1:
                # if we are fetching one thing itll return
                # i instead of (i, )

                d = d[0]

            return d

    async def fetchmany(self, i, *args, **kwargs):
        """Wrapper for single fetchmany call"""
        async with self.__pool.acquire() as conn:
            c = await conn.cursor()
            await c.execute(*args, **kwargs)

            return await c.fetchmany(i)
