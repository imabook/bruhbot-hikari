from datetime import datetime, timedelta
from utils.database import Database
from database.queries import *


# i really need to make this a class and provide the pool one time instead of providing it in each fucking call 😩
async def register_user(pool: Database, id: int, date: datetime) -> None:
    await pool.execute(STORE_USER, (id, date))
    await pool.execute(STORE_ECONOMY, (id, ))
    await pool.execute(STORE_ECONOMY_REBIRTH, (id, ))


async def store_item(pool: Database, id: int, item_id: int) -> None:
    await pool.execute(STORE_ITEM, (id, item_id))


async def update_coins(pool: Database, id: int, i: int) -> None:
    await pool.execute(UPDATE_COINS, (i, id))


async def update_coins_add(pool: Database, id: int, i: int) -> None:
    await pool.execute(UPDATE_COINS_ADD, (i, id))


async def update_coins_subtract(pool: Database, id: int, i: int) -> None:
    await pool.execute(UPDATE_COINS_SUB, (i, id))


async def update_prays(pool: Database, id: int) -> None:
    await pool.execute(UPDATE_PRAYS, (id, ))


async def update_religion(pool: Database, id: int, name: str) -> None:
    await pool.execute(UPDATE_RELIGION, (name, id))


async def update_xp(pool: Database, id: int, i: int) -> None:
    await pool.execute(UPDATE_XP, (i, id))


async def update_lvl(pool: Database, id: int, lvl: int, xp: int) -> None:
    await pool.execute(UPDATE_LVL, (lvl, xp, id))


async def update_abuelas_add(pool: Database, id: int) -> None:
    await pool.execute(
        "UPDATE economy SET abuelas = abuelas + 1 WHERE id = %s", (id, ))


async def update_iglesias_add(pool: Database, id: int) -> None:
    await pool.execute(
        "UPDATE economy SET iglesias = iglesias + 1 WHERE id = %s", (id, ))


async def update_items_add(pool: Database, id: int, item_id: int) -> None:
    await pool.execute(UPDATE_ITEMS_ADD, (id, item_id))


async def update_items_sub(pool: Database, id: int, item_id: int) -> None:
    await pool.execute(UPDATE_ITEMS_SUB, (id, item_id))


async def fetch_amuletos(pool: Database, id: int) -> int:
    return await pool.fetchone(FETCH_AMULETOS, (id, ))


async def fetch_coins(pool: Database, id: int) -> int:
    return await pool.fetchone(FETCH_COINS, (id, ))


async def fetch_prays(pool: Database, id: int) -> int:
    return await pool.fetchone(FETCH_PRAYS, (id, ))


async def fetch_level(pool: Database, id: int):
    return await pool.fetchone(FETCH_LVL, (id, ))


async def fetch_level_only(pool: Database, id: int):
    return await pool.fetchone(FETCH_LVL_ONLY, (id, ))


async def fetch_prayinfo(pool: Database, id: int):
    user_info = await pool.fetchone(FETCH_PRAYINFO_USER, (id, ))

    economy_info = await fetch_user_shop(pool, id)

    return (user_info, economy_info)


async def fetch_religion(pool: Database, id: int) -> str:
    return await pool.fetchone(FETCH_RELIGION, (id, ))


async def fetch_shop(pool: Database):
    return await pool.fetchone(FETCH_SHOP)


async def fetch_user_shop(pool: Database, id: int):
    return await pool.fetchone(FETCH_PRAYINFO_ECONOMY, (id, ))


async def fetch_user_item(pool: Database, id: int, item_id: int):
    return await pool.fetchone(FETCH_USER_ITEM, (id, item_id))


async def fetch_user_items(pool: Database, id: int, item_id: int):
    return await pool.fetch(FETCH_USER_ITEMS, (id, ))


async def make_transaction(pool: Database, author_id: int, other_id: int,
                           author_coins: int, other_coins: int,
                           amount: int) -> None:
    await update_coins(pool, author_id, author_coins - amount)
    await update_coins(pool, other_id, other_coins + amount)

    await pool.execute(UPDATE_GIVEN, (amount, author_id))
    await pool.execute(UPDATE_RECIEVED, (amount, other_id))

    # await pool.execute(STORE_TRANSACTION, (author_id, other_id, amount, time))


async def buy_object(pool: Database,
                     id: int,
                     coins: int,
                     name: str,
                     amount: int = 1) -> None:
    QUERY = UPDATE_ECONOMY_OBJECT.replace("$ROW", name)

    await pool.execute(QUERY, (coins, amount, id))


async def validate_user(pool: Database, id: int) -> bool:
    """ RETURNS TRUE WHEN THE USER EXISTS IN THE DB, RETURNS FALSE OTHERWISE """
    return await pool.fetchone("SELECT id FROM users WHERE id = %s;",
                               (id, )) != None


async def get_timeout(pool: Database, id: int) -> int:
    i = await pool.fetchone(FETCH_TIMEOUT, (id, ))

    if i == None:
        await pool.execute(STORE_TIMEOUT, (id, datetime.utcnow().timestamp()))

        return 0

    seconds = datetime.utcnow().timestamp() - i

    if seconds >= 86400:
        # 86400 seconds in a day
        await pool.execute(UPDATE_TIMEOUT, (datetime.utcnow().timestamp(), id))
        return 0

    # returning the amount of seconds the user has to wait for cooldown to end
    return 86400 - seconds


async def get_item_info(pool: Database, id: int):
    return await pool.fetchone(
        "SELECT name, description FROM items WHERE id = %s", (id, ))
