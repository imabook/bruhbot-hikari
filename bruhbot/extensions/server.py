import lightbulb
import hikari
from lightbulb.ext import tasks

import os
from dotenv import load_dotenv

from aiohttp import web

from core.bot import BruhApp

plugin = lightbulb.Plugin("server")
plugin.add_checks(lightbulb.guild_only)

load_dotenv()

app = web.Application()
routes = web.RouteTableDef()


@routes.post('/dbl')
async def handle_dbl(r: web.Request):

    if not r.headers.get('Authorization') == os.environ["DBL_PASS"]:
        # unauth request to the bot (not top.gg ⚠️)
        print("unauth request !!")
        return web.StreamResponse(status=200)

    user_id = (await r.json())["user"]

    # para ver si ha rezado almenos una vez
    if await r.app.bot.db.validate_user(user_id):

        # 6 is the id of the voter item
        await r.app.bot.db.update_user_items(user_id, 6, "add")

        # m enudo tochardo para solo mandar un dm
        try:
            await r.app.bot.rest.create_message(
                await (await
                       r.app.bot.rest.fetch_user(user_id)).fetch_dm_channel(),
                "muchas gracias por votarme\ncomo eres muy humilde ahora ganas más xp y has conseguido **<:voted:1125748821574557749> voto de fe**"
            )

        except Exception as e:
            print(e)
    # else:
    #     try:
    #         await r.app.bot.rest.create_message(
    #             await (await
    #                    r.app.bot.rest.fetch_user(user_id)).fetch_dm_channel(),
    #             "se viene update... ‼️")

    #     except Exception as e:
    #         print(e)

    return web.StreamResponse(status=200)


@tasks.task(s=5, pass_app=True, max_executions=1)
async def webserver(bot: BruhApp):
    app.bot = bot

    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=os.environ["DBL_PORT"])
    await site.start()

    webserver.stop()


def load(bot: BruhApp):

    bot.add_plugin(plugin)

    if not webserver.is_running:
        webserver.start()

    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
