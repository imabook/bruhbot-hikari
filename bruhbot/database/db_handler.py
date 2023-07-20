from datetime import datetime, timedelta
from utils.database import Database
from database.queries import *

import lightbulb

import aiofiles
import json
import math
import random

class DBHandler:

    def __init__(self, pool: Database):
        self.pool = pool

    # i really need to make this a class and provide the pool one time instead of providing it in each fucking call 😩
    async def register_user(self, id: int, date: datetime) -> None:
        await self.pool.execute(STORE_USER, (id, date))
        await self.pool.execute(STORE_ECONOMY, (id, ))
        await self.pool.execute(STORE_ECONOMY_REBIRTH, (id, ))

    async def update_coins(self, id: int, i: int) -> None:
        await self.pool.execute(UPDATE_COINS, (i, id))

    async def update_coins_add(self, id: int, i: int) -> None:
        await self.pool.execute(UPDATE_COINS_ADD, (i, id))

    async def update_coins_subtract(self, id: int, i: int) -> None:
        await self.pool.execute(UPDATE_COINS_SUB, (i, id))

    async def update_prays(self, id: int) -> None:
        await self.pool.execute(UPDATE_PRAYS, (id, ))

    async def update_religion(self, id: int, name: str) -> None:
        await self.pool.execute(UPDATE_RELIGION, (name, id))

    async def update_xp(self, id: int, i: int) -> None:
        await self.pool.execute(UPDATE_XP, (i, id))

    async def update_lvl(self, id: int, lvl: int, xp: int) -> None:
        await self.pool.execute(UPDATE_LVL, (lvl, xp, id))

    async def update_abuelas_add(self, id: int) -> None:
        await self.pool.execute(
            "UPDATE economy SET abuelas = abuelas + 1 WHERE id = %s", (id, ))

    async def update_iglesias_add(self, id: int) -> None:
        await self.pool.execute(
            "UPDATE economy SET iglesias = iglesias + 1 WHERE id = %s", (id, ))

    async def update_user_items(self, id: int, item_id: int,
                                amount: int | str) -> None:
        
        item_id = int(item_id)

        # tambien se puede usar con "add" o "sub" en amount para mas facil uso 👍
        if type(amount) == str:
            temp_amount = await self.fetch_item_amount(id, item_id) or 0 # because it can return None

            match amount:
                case "add":
                    temp_amount += 1
                case "sub":
                    temp_amount -= 1
                    

            amount = temp_amount

        if amount == 0:
            await self.pool.execute(DELETE_USER_ITEM, (id, item_id))

            return

        if await self.pool.fetchone(
                "SELECT amount FROM user_items WHERE user_id = %s AND item_id = %s",
            (id, item_id)) == None:
            # significa que no existe en la base de datos, asiqeu creamos la entrada
            await self.pool.execute(STORE_ITEM, (id, item_id, amount))
            return

        # sino pues se actualiza rechulon
        await self.pool.execute(UPDATE_USER_ITEM, (amount, id, item_id))

    async def fetch_amuletos(self, id: int) -> int:
        return await self.pool.fetchone(FETCH_AMULETOS, (id, ))

    async def fetch_coins(self, id: int) -> int:
        return await self.pool.fetchone(FETCH_COINS, (id, ))

    async def fetch_prays(self, id: int) -> int:
        return await self.pool.fetchone(FETCH_PRAYS, (id, ))

    async def fetch_level(self, id: int):
        return await self.pool.fetchone(FETCH_LVL, (id, ))

    async def fetch_level_only(self, id: int):
        return await self.pool.fetchone(FETCH_LVL_ONLY, (id, ))

    async def fetch_prayinfo(self, id: int):
        user_info = await self.pool.fetchone(FETCH_PRAYINFO_USER, (id, ))

        economy_info = await self.fetch_user_shop(id)

        return (user_info, economy_info)

    async def fetch_religion(self, id: int) -> str:
        return await self.pool.fetchone(FETCH_RELIGION, (id, ))

    async def fetch_shop(self: Database):
        return await self.pool.fetchone(FETCH_SHOP)

    async def fetch_user_shop(self, id: int):
        return await self.pool.fetchone(FETCH_PRAYINFO_ECONOMY, (id, ))

    async def fetch_user_items(self, id: int):
        return await self.pool.fetch(FETCH_USER_ITEMS, (id, ))

    async def fetch_item_amount(self, user_id: int, item_id: int):
        return await self.pool.fetchone(FETCH_ITEM_AMOUNT, (user_id, item_id))

    async def fetch_item_info(self, ids: set[int]):
        # ni idea de porque lo hice asi pero bueno funciona con la logica del pray.py
        # ah ya me acuerdo es para luego hacer el dict bien con el amount de items
        # si tiene sentido 👍

        if type(ids) == int:
            ids = (ids)

        async with aiofiles.open("./bruhbot/json/items.json", mode="r", encoding="utf8") as f:
            items = json.loads(await f.read())

            # no necesita el str(i) pero por si acaso
            return [[i] + list(items[str(i)].values()) for i in ids]

    async def fetch_item_from_tier(self, tier: int):
        async with aiofiles.open("./bruhbot/json/items.json", mode="r", encoding="utf8") as f:
            items = json.loads(await f.read())

            # output: [["1", {...}], ...]
            return [[key] + [i] for key, i in items.items() if i["tier"] == tier]

    async def fetch_item_from_tiers(self, tiers: set[int]):
        if type(tiers) == int:
            tiers = (tiers, )
        # fetches all items except special ones (aka tier 0, 5)
        async with aiofiles.open("./bruhbot/json/items.json", mode="r", encoding="utf8") as f:
            items = json.loads(await f.read())

            # output: [["1", {...}], ...]
            return [[key] + [i] for key, i in items.items() if i["tier"] in tiers]

    async def fetch_user_missions(self, id: int):
        weekly = await self.pool.fetchone(FETCH_USER_MISSIONS_WEEKLY, (id, ))
        
        if not weekly:
            return list(await self.pool.fetch(FETCH_USER_MISSIONS, (id, )))

        return [weekly] + list(await self.pool.fetch(FETCH_USER_MISSIONS, (id, )))

    async def fetch_mission_info(self, ids: set[int]):
        if type(ids) == int:
            ids = (ids, )

        missions = await self.pool.fetch(FETCH_MISSION_INFO, (ids,))
                # {mission_id: 'nombre'}
        return {m[0]: m[1] for m in missions}

    async def make_transaction(self, author_id: int, other_id: int,
                               author_coins: int, other_coins: int,
                               amount: int) -> None:
        await self.update_coins(author_id, author_coins - amount)
        await self.update_coins(other_id, other_coins + amount)

        await self.pool.execute(UPDATE_GIVEN, (amount, author_id))
        await self.pool.execute(UPDATE_RECIEVED, (amount, other_id))

        # await self.pool.execute(STORE_TRANSACTION, (author_id, other_id, amount, time))

    async def buy_object(self,
                         id: int,
                         coins: int,
                         name: str,
                         amount: int = 1) -> None:
        QUERY = UPDATE_ECONOMY_OBJECT.replace("$ROW", name)

        await self.pool.execute(QUERY, (coins, amount, id))

    async def validate_user(self, id: int) -> bool:
        """ RETURNS TRUE WHEN THE USER EXISTS IN THE DB, RETURNS FALSE OTHERWISE """
        return await self.pool.fetchone("SELECT id FROM users WHERE id = %s;",
                                        (id, )) != None

    async def get_timeout(self, id: int) -> int:
        i = await self.pool.fetchone(FETCH_TIMEOUT, (id, ))

        if i == None:
            await self.pool.execute(STORE_TIMEOUT,
                                    (id, datetime.utcnow().timestamp()))

            return 0

        seconds = datetime.utcnow().timestamp() - i

        if seconds >= 86400:
            # 86400 seconds in a day
            await self.pool.execute(UPDATE_TIMEOUT,
                                    (datetime.utcnow().timestamp(), id))
            return 0

        # returning the amount of seconds the user has to wait for cooldown to end
        return 86400 - seconds

    async def handle_xp(self, ctx: lightbulb.Context, id: int, bonus: int = 0):
        lvl, xp = await self.fetch_level(id)
        max = self.get_max_xp(lvl)

        # get other bonus multipliers
        bonus += lvl // 10

        xp_add = random.randint(1, 5) + bonus

        if await ctx.bot.has_user_voted(id):
            xp_add = math.ceil(xp_add * 1.2)  # the 20% of xp if the mf voted

        new_xp = xp_add + xp

        if new_xp >= max:
            next_max = self.get_max_xp(lvl + 1)
            new_xp -= max

            if new_xp >= next_max:
                # prevent more than one lvl up
                new_xp = next_max - 1

            await self.update_lvl(id, lvl + 1, new_xp)
            await ctx.respond(
                f"{random.choice(['espera espera', 'el diablo', 'yoooo', 'mira', 'enhorabuena'])}, has subido al nivel **{lvl + 1}** 😎🎉"
            )
        else:
            await self.update_xp(id, new_xp)


    def get_max_xp(self, i: int) -> int:
        return math.ceil(((i + 1)**1.2) * 10)
