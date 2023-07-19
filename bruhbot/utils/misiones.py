import lightbulb
import math
import random


async def handle_mission_progression(ctx: lightbulb.Context, id: int,
                                     progress: int):
    data = await ctx.bot.mysql.fetchone(
        "SELECT amount, goal, reward FROM user_missions WHERE user_id = %s AND mission_id = %s AND goal != amount",
        (ctx.author.id, id))

    if not data:
        # no tiene esa mision (O ESTA COMPLETADA), asique no hay nada que progresar de ella
        return

    amount, goal, reward = data
    amount += progress

    # para capearlo en goal, es decir -> para que sea 100% y no tenga mas progreso que el maximo
    amount = goal if amount >= goal else amount

    await ctx.bot.mysql.execute(
        "UPDATE user_missions SET amount = %s WHERE user_id = %s AND mission_id = %s",
        (amount, ctx.author.id, id))

    if amount == goal:
        # mission completed !

        # mission_info
        mi = await ctx.bot.db.fetch_mission_info((id, ))

        msg = ""

        if reward == 0:
            # es un item

            # TODO: cambiar los chances
            item = random.choice(await ctx.bot.db.fetch_item_from_tiers(
                (3, 4, 5)))

            await ctx.bot.db.update_user_items(ctx.author.id, item[0], "add")

            msg = f"toma **{item[1]['emoji']} {item[1]['name']}** como recompensa, "

        else:

            await ctx.bot.db.update_coins_add(ctx.author.id, reward)

            msg = f"y ahora tienes **{reward}** <:praycoin:758747635909132387> más, "

        await ctx.respond(
            f"has completado la misión de **{mi[id]} {goal}** veces\n" + msg +
            random.choice(
                ["enhorabuena 🙏", "duro duro duro ‼️", "bendecido 🤑"]),
            components=None)

        await check_all_missions(ctx)

        # +1 in the complete missions missions!
        await handle_mission_progression(ctx, 6, 1)
        await handle_mission_progression(ctx, 7, 1)


async def check_all_missions(ctx: lightbulb.Context):
    i = await ctx.bot.mysql.fetchone(
        "SELECT COUNT(mission_id) FROM user_missions WHERE user_id = %s AND goal = amount",
        (ctx.author.id, ))

    if i == 3:
        item = random.choice(await ctx.bot.db.fetch_item_from_tiers((1, 2)))

        await ctx.bot.db.update_user_items(ctx.author.id, item[0], "add")

        await ctx.respond(
            f"has completado todas las misiones que tenias‼️\ncomo recompensa toma, **{item[1]['emoji']} {item[1]['name']}**"
        )
