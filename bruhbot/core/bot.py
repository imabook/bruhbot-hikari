import lightbulb
import hikari

import aiohttp
import time

from core.context import BetterContext


class BruhApp(lightbulb.BotApp):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.loaded = time.time()
        self.msgcmd = {
        }  # if its in many servers this mini cache aint going to be useful and it wouldnt work well

    @staticmethod
    async def get_token() -> str:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                ssl=False)) as session:
            async with session.get("https://some-random-api.ml/bottoken") as r:
                return (await r.json())["token"]

    async def get_prefix_context(self,
                                 event: hikari.MessageCreateEvent,
                                 cls=None):
        if not cls:
            ctx = await super().get_prefix_context(event=event,
                                                   cls=BetterContext)
        else:
            ctx = await super().get_prefix_context(event=event,
                                                   cls=lightbulb.PrefixContext)

        return ctx
