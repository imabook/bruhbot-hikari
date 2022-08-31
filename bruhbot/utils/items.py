import math
import random

from database.db_handler import *
from utils.database import Database

async def get_utility(pool: Database, id: int, user_id: int):
    match id:
        case 1:
            coins = random.randint(50, 200)
            await update_coins_add(pool, user_id, coins)

            return coins
        case 2:
            await update_abuelas_add(pool, user_id)
            return
        case 3:
            await update_iglesias_add(pool, user_id)
            return
        case 4:
            a, i = await pool.fetchone("SELECT abuelas, iglesias FROM economy WHERE id = %s", (id,))
            await update_coins_add(pool, user_id, a * (i + 1))

def get_emoji(i: int):
    # provisional emojis
    match i:
        case 1:
            return "💰"
        case 2:
            return "👵"
        case 3:
            return "🏛️"
        case 4:
            return "🔔"