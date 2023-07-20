import lightbulb
import hikari

import asyncio
import time

from utils.database import Database
from core.context import BetterContext

from aiohttp import web, ClientSession
from cache import AsyncTTL

import os
from dotenv import load_dotenv
import threading
import aiomysql

load_dotenv()


class BruhApp(lightbulb.BotApp):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.mysql: Database
        self.loaded = time.time()

    @AsyncTTL(time_to_live=300, maxsize=5120)
    async def has_user_voted(self, user_id) -> bool:
        """returns true if the user has voted, it has a 5 minute cache so it might not be 100% accurate but its fine"""

        headers = {"Authorization": os.environ["DBL_TOKEN"]}
        async with ClientSession(headers=headers) as session:
            async with session.get(
                    f"https://top.gg/api/bots/693163993841270876/check?userId={user_id}"
            ) as r:

                if r.status != 200:
                    return False

                try:
                    response = await r.json()
                except:
                    return False

                return response["voted"] == 1
