import math
import random
from datetime import datetime, timedelta

import miru

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

from database.db_handler import *

async def use_item(ctx: miru.Context, id: int):
    match id:
        case 1:
            # hacer que te pueda hacer drop de otro item o algo! !
            if random.randint(1, 50) == 1:
                await ctx.bot.db.update_coins_add(ctx.author.id, 1)

                await ctx.edit_response("la cartera tenia **1** <:praycoin:758747635909132387> <:troll:826403463062749224>", components=None)
            else:
                # directito del daily xd
                ei = await ctx.bot.db.fetch_user_shop(ctx.author.id)
                pph = ei[1] * (ei[2] + 1) + ei[4] * 10 * (ei[5] + 1)

                coins = random.randint(pph + 2, (pph + 2) * 5)
                await ctx.bot.db.update_coins_add(ctx.author.id, coins)

                await ctx.edit_response(random.choice([f"has joseado **{coins}** <:praycoin:758747635909132387>", f"dentro de la cartera habían **{coins}** <:praycoin:758747635909132387>", f"buah **{coins}** <:praycoin:758747635909132387> más para ti", f"ahora tienes **{coins}** <:praycoin:758747635909132387> más, no lo apuestes 😈‼️"]), components=None)

            return
        case 2:
            await ctx.bot.db.update_abuelas_add(ctx.author.id)
            shop = await ctx.bot.db.fetch_user_shop(ctx.author.id)
            await ctx.edit_response(f"se ha unido una abuela mas a tu religión, ahora tienes **{shop[1]}**", components=None)

            return
        case 3:
            await ctx.bot.db.update_iglesias_add(ctx.author.id)
            shop = await ctx.bot.db.fetch_user_shop(ctx.author.id)
            await ctx.edit_response(f"se ha unido una abuela mas a tu religión, ahora tienes **{shop[2]}**", components=None)

            return
        case 4:
            a, i = await ctx.bot.mysql.fetchone("SELECT abuelas, iglesias FROM economy WHERE id = %s", (id,))
            await ctx.bot.db.update_coins_add(ctx.author.id, a * (i + 1))

            await ctx.edit_response(f"todas tus abuelas han rezado y has conseguido **{a * (i + 1)}** <:praycoin:758747635909132387>", components=None)
            return
        case 5:
            members =[m.id async for m in ctx.bot.rest.fetch_members(ctx.guild_id) if not m.is_bot and m.id != ctx.author.id]

            ids = await ctx.bot.mysql.fetch("SELECT id FROM users WHERE id IN %s ORDER BY RAND();", (members,))

            if len(ids) >= 10:
            
                winner = ids[0][0]
                msg = ""

                if random.randint(0, 4) == 0:
                    # item drop
                    item = random.choice(await ctx.bot.db.fetch_item_from_tier(1))
                    await ctx.bot.db.update_user_items(winner, int(item[0]), "add")

                    msg = f"**{item[1]['emoji']} {item[1]['name']}**"
                else:

                    coins = random.randint(1000, 5000)
                    await ctx.bot.db.update_coins_add(winner, coins)

                    msg = f"**{coins}** <:praycoin:758747635909132387>"

                await ctx.edit_response(random.choice([f"abres el regalo humilde y <@{winner}> se lleva {msg}", f"<@{winner}> se ha llevado {msg} de tu regalo humilde", f"{msg} para <@{winner}> gracias a tu regalo humilde ‼️"]), components=None)

                return


            await ctx.bot.db.update_user_items(ctx.author.id, 5, "add")

            await ctx.edit_response("en este server hay muy pocas personas que usan el bot, no puedes usar este item aquí", components=None)
            return

        case 6:
            if random.randint(0, 4) == 0:
                # item drop
                tier = 1 if random.randint(0, 99) < 70 else 2
                item = random.choice(await ctx.bot.db.fetch_item_from_tier(tier))
                await ctx.bot.db.update_user_items(ctx.author.id, int(item[0]), "add")

                msg = f"**{item[1]['emoji']} {item[1]['name']}**"
            else:
                # directito del item 1 xd
                # directito del daily xd
                ei = await ctx.bot.db.fetch_user_shop(ctx.author.id)
                pph = ei[1] * (ei[2] + 1) + ei[4] * 10 * (ei[5] + 1)

                coins = random.randint((pph + 1) * 2, (pph + 1) * 4)

                await ctx.bot.db.update_coins_add(ctx.author.id, coins)

                msg = f"**{coins}** <:praycoin:758747635909132387>"


            await ctx.edit_response(f"muchas gracias por votar enserio 🙏\nhas conseguido {msg} ‼️", components=None)
            return

        case 7:
            missions = await ctx.bot.mysql.fetch("SELECT mission_id, ends_at FROM user_missions WHERE user_id = %s ORDER BY ends_at", (ctx.author.id))

            if not missions or len(missions) < 3:
                await ctx.edit_response("no tienes ninguna misión, como quieres que te las resetee?", components=None)
                await ctx.bot.db.update_user_items(ctx.author.id, 7, "add")

                return
            
            lvl = await ctx.bot.db.fetch_level_only(ctx.author.id)

            await ctx.bot.mysql.execute("DELETE FROM user_missions WHERE user_id = %s", (ctx.author.id,))
            await ctx.bot.mysql.execute("""
INSERT INTO user_missions (user_id, mission_id, ends_at, reward, goal)
        SELECT 
            %s, 
            m.id, 
            %s, 
            CEIL((RAND() * (1500 - 850) + 850) * %s/4), 
            IF(m.is_modular, 
                CEIL(%s * (RAND() * (m.max_amount - m.min_amount) + m.min_amount)), 
                CEIL(RAND() * (m.max_amount - m.min_amount) + m.min_amount)
            )
        FROM (
            SELECT id, min_amount, max_amount, is_modular
            FROM missions
            WHERE is_7d = false AND id NOT IN (%s, %s)
            ORDER BY RAND()
            LIMIT 2
        ) m;
""", (ctx.author.id, missions[0][1], lvl, lvl, missions[0][0], missions[1][0]))
            
            await ctx.bot.mysql.execute("""
INSERT INTO user_missions (user_id, mission_id, ends_at, reward, goal)
        SELECT 
            %s, 
            m.id, 
            %s, 
            0, 
            IF(m.is_modular, 
                CEIL(%s * (RAND() * (m.max_amount - m.min_amount) + m.min_amount)), 
                CEIL(RAND() * (m.max_amount - m.min_amount) + m.min_amount)
            )
        FROM (
            SELECT id, min_amount, max_amount, is_modular
            FROM missions
            WHERE is_7d = true AND id != %s
            ORDER BY RAND()
            LIMIT 1
        ) m;
""", (ctx.author.id, missions[2][1], lvl, missions[2][0]))

            await ctx.edit_response(random.choice(["no te gustaban las otras o que?", "las otras eran jodidas ehh"]) + "\nbueno da igual ya tienes misiones nuevas", components=None)
            return

        case 8:
            mission = await ctx.bot.mysql.fetchone("SELECT mission_id, goal, reward FROM user_missions WHERE user_id = %s AND amount != goal ORDER BY RAND();", (ctx.author.id, ))
            print(mission)

            if not mission:
                await ctx.edit_response("loco ya tienes todas las misiones hechas, no puedo completar ninguna por ti", components=None)
                await ctx.bot.db.update_user_items(ctx.author.id, 8, "add")

                return
            
            info = await ctx.bot.db.fetch_mission_info((mission[0], ))
            await ctx.bot.mysql.execute("UPDATE user_missions SET amount = goal WHERE user_id = %s AND mission_id = %s", (ctx.author.id, mission[0]))

            msg = f"\nah y has conseguido "
            if mission[2] == 0:
                # el reward es un item            
                # TODO: cambiar los chances
                item = random.choice(await ctx.bot.db.fetch_item_from_tiers(
                (3, 4, 5)))

                await ctx.bot.db.update_user_items(ctx.author.id, item[0], "add")
                msg += f"**{item[1]['emoji']} {item[1]['name']}**"
            else:
                await ctx.bot.db.update_coins_add(ctx.author.id, mission[2])

                msg += f"**{mission[2]}** <:praycoin:758747635909132387>"

            i = await ctx.bot.mysql.fetchone(
                "SELECT COUNT(mission_id) FROM user_missions WHERE user_id = %s AND goal = amount",
                (ctx.author.id, ))

            print(i)
            if i == 3:
                # mensaje especial de cuando ya completa todas las misiones
                item = random.choice(await ctx.bot.db.fetch_item_from_tiers((1, 2)))

                await ctx.bot.db.update_user_items(ctx.author.id, item[0], "add")

                await ctx.edit_response(f"hecho, justo era la ultima misión que te quedaba no?\nporque has conseguido **{item[1]['emoji']} {item[1]['name']}** como recompensa bonus o algo" + msg + "de la misión nomral, claro")

                return

            await ctx.edit_response(f"he hecho la misión que decía **{info[mission[0]]} {mission[1]} veces** o algo así por ti, " + random.choice(["disfruta", "ahora tienes una menos", "no era tan dificil en verdad"]) + msg , components=None)


        case 9:
            await ctx.bot.db.update_coins_add(ctx.author.id, 1000000)
            await ctx.edit_response("solo los reales se acuerdan de la **piedra pana** 😔\nte ha dado **1.000.000** <:praycoin:758747635909132387> fr 😨‼️", components=None)
            return
        case 10:
            item = random.choice(await ctx.bot.db.fetch_item_from_tiers((1, 2, 3, 4)))
            await ctx.bot.db.update_user_items(ctx.author.id, int(item[0]), "add")

            if int(item[0]) == 10:
                await ctx.edit_response(f"de forma TOTALMENTE aleatoria sin ningun tipo de ALGORITMO tu {item[1]['emoji']} **{item[1]['name']}** te ha dado otro {item[1]['emoji']} **{item[1]['name']}**‼️", components=None)

                return

            await ctx.edit_response(random.choice([f"te ha tocado un {item[1]['emoji']} **{item[1]['name']}**, esta bien no?", f"he tirado el dado y ha salido un {item[1]['emoji']} **{item[1]['name']}**", f"pues ahora tienes otro {item[1]['emoji']} **{item[1]['name']}**, no puedes volver a tirar el dado es lo que hay"]), components=None)


        case 11:
            # deberia de activamente borrar los timeouts ya pasados para ahorrar espacio
            await ctx.bot.mysql.execute("DELETE FROM timeouts WHERE id = %s", (ctx.author.id, ))

            d = datetime.now() + timedelta(days=1)

            await ctx.edit_response(random.choice(["buah que rayada", "ehh perdona perdona", "pues sí, tienes razón", "locurote"]) + f" parece que ya es **{d.day}** de **{MESES[d.month - 1]}**\nya puedes hacer el </daily:1014611874807042138> otra vez", components=None)
            return

        case 12:
            await ctx.edit_response("has conseguido algo de xp", components=None)
            await ctx.bot.db.handle_xp(ctx, ctx.author.id, random.randint(4, 8))

            return 

        case 13:
            await ctx.bot.mysql.execute("UPDATE users SET lvl = lvl + 1, xp = 0 WHERE id = %s", (ctx.author.id, ))
            
            lvl = await ctx.bot.db.fetch_level_only(ctx.author.id)

            await ctx.edit_response(f"¡**{ctx.author.username.upper()}** ha subido al nivel **{lvl}**!", components=None)
            return

        case _:
            await ctx.edit_response("en verdad no tengo ni idea de que hace este item", components=None)
