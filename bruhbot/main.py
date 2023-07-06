import hikari
from hikari import Intents
import lightbulb
import miru

from lightbulb.ext import tasks

import os
import datetime
import aiomysql
import logging
import threading
import asyncio
from dotenv import load_dotenv
from contextlib import suppress

import random
from aiohttp import web
from utils.database import Database
from database.db_handler import DBHandler

from core.embed import BetterEmbed
from core.bot import BruhApp

load_dotenv()

intents = (Intents.GUILDS | Intents.GUILD_MEMBERS
           | Intents.GUILD_EMOJIS | Intents.ALL_MESSAGES
           | Intents.GUILD_MESSAGE_REACTIONS | Intents.ALL_MESSAGE_TYPING)

# def prefix(app: BruhApp, message: hikari.Message):
#     if message.author and message.author.id in [
#             424213584659218445, 436521909144911874, 506565592757698600
#     ]:
#         return ["", "bruh "]

#     return "bruh"

bot = BruhApp(
    token=os.environ["TEST_TOKEN"],
    intents=intents,
    # prefix=prefix,
    owner_ids=[424213584659218445, 436521909144911874],
    # case_insensitive_prefix_commands=True,
    help_class=None,
    cache_settings=hikari.impl.CacheSettings(
        components=hikari.api.CacheComponents.GUILDS),
)

miru.install(bot)
tasks.load(bot)


@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option(
    "plugin",
    "Plugin para cargar",
    choices=[
        e.replace("extensions.", "").capitalize() for e in bot.extensions
    ],
)
@lightbulb.command("load", "Carga el plugin especificado", hidden=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def load(ctx):
    if not ctx.options.plugin:
        return await ctx.respond("pero dime que plugin cargar no?")

    try:
        bot.load_extensions(f"extensions.{ctx.options.plugin}".lower())
        await ctx.respond("hecho rey <:tula:748526797913849956>")
    except Exception as e:
        await ctx.respond(f"semihecho supongo xd:\n```fix\n{e}\n```")


@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("plugin",
                  "Plugin para cargar",
                  choices=[
                      e.replace("extensions.", "").capitalize()
                      for e in bot.extensions
                  ])
@lightbulb.command("unload", "Elimina el plugin especificado", hidden=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def unload(ctx):
    if not ctx.options.plugin:
        return await ctx.respond("pero dime que plugin eliminar no?")

    try:
        bot.unload_extensions(f"extensions.{ctx.options.plugin}".lower())
        await ctx.respond("hecho rey <:tula:748526797913849956>")
    except Exception as e:
        await ctx.respond(f"semihecho supongo xd:\n```fix\n{e}\n```")


@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("reload", "Recarga todos los plugins", hidden=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def reload(ctx: lightbulb.Context):
    try:
        [
            bot.reload_extensions(f"extensions.{i[:-3]}")
            for i in os.listdir("./bruhbot/extensions/") if i.endswith(".py")
        ]
        await ctx.respond("hecho rey <:tula:748526797913849956>")
    except Exception as e:
        await ctx.respond(f"semihecho supongo xd:\n```fix\n{(e)}\n```")


@bot.listen(hikari.StartedEvent)
async def on_connect(event: hikari.StartedEvent):

    # load them database connection
    pool = await aiomysql.create_pool(host=os.environ["HOST"],
                                      port=int(os.environ["PORT"]),
                                      user=os.environ["USER"],
                                      password=os.environ["PASSWORD"],
                                      db=os.environ["DB"],
                                      autocommit=True)

    bot.mysql = Database(pool)
    bot.db = DBHandler(bot.mysql)

    # load them cogs
    [
        bot.load_extensions(f"extensions.{i[:-3]}")
        for i in os.listdir("./bruhbot/extensions/") if i.endswith(".py")
    ]


@bot.listen(hikari.StoppingEvent)
async def on_disconnect(event: hikari.StoppingEvent):
    # se supone que se triggea justo antes de que el bot se desconecte (supongo que si discord fuerza que el bot se desconecte no avisara)
    try:
        await bot.mysql.close()

        # await bot.web_app.shutdown()
        # await bot.web_app.cleanup()
    except Exception as e:
        print(e)

    await event.app.rest.create_message(717008102175539231,
                                        "RIP <@424213584659218445>",
                                        user_mentions=True)
    # await channel.send()


@bot.listen(hikari.GuildJoinEvent)
async def on_guild_join(event: hikari.GuildJoinEvent):

    embed = BetterEmbed(
        title="Ehh pero bueno, muchas gracias por invitarme 😳",
        description="Aquí tienes alguna información sobre mí 😎",
        color=0x5755d6
    ).add_field(
        name="Para empezar:",
        value=
        "Para ver la lista de comandos solo haz `/help`\nSi quieres rezar y todo eso haz `/pray`"
    ).add_field(
        name="Otras cosas:",
        value=
        "Si tienes algunos problemas con comandos, o tienes sugerencias para que este bot no sea tan mierda, únete al [server](https://discord.gg/qB7p97H) del bot"
    )

    fetch_channels = [
        c for c in await event.app.rest.fetch_guild_channels(event.guild_id)
        if c.type == 0
    ]

    channels = [
        c for c in fetch_channels if c.name in ["bot", "commands", "comandos"]
    ]

    if channels:
        for channel in channels:
            try:
                await channel.send(embed=embed)
                return
            except Exception:
                pass

    channels = [
        c for c in fetch_channels
        if c.name in ["general", "chill", "vibe", "chat", "lobby", "main"]
    ]

    if channels:
        for channel in channels:
            try:
                await channel.send(embed=embed)
                return
            except Exception:
                pass

    for channel in fetch_channels:
        try:
            await channel.send(embed=embed)
            return
        except Exception:
            pass


@bot.listen(hikari.MemberCreateEvent)
async def on_member_join(event: hikari.MemberCreateEvent):
    if event.guild_id == 707958627377348719:
        await event.member.add_role(784532927446384720)

        await event.app.rest.create_message(
            channel=761970663840940073,
            content="➡️ " + random.choice([
                f"muy buenas {event.member.mention} 🐠",
                f"se unió un ludópata, bienvenido {event.member.mention}",
                f"{event.member.mention}, este chaval fuma seguro 😇🚬",
                f"{event.member.mention} es un real más",
                f"que grande eres {event.member.mention}",
                f"{event.member.mention} se unió a la gang"
            ]),
            user_mentions=False)


@bot.listen(hikari.MemberDeleteEvent)
async def on_member_leave(event: hikari.MemberDeleteEvent):
    if event.guild_id == 707958627377348719:

        name = (await event.app.rest.fetch_user(event.user_id)).username

        await event.app.rest.create_message(
            channel=761970663840940073,
            content="⬅️ " + random.choice([
                f"a **{name}** le dió sueño 💤",
                f"**{name}**, este chaval no fuma seguro 👿🚭",
                f"**{name}** ha traicionado a la banda",
                f"**{name}** simplemente no le sabe",
                f"no hay canal nsfw y **{name}** se fué"
            ]),
            user_mentions=False)


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent):
    await _handle_error(event.context, event.exception)


async def _handle_error(ctx: lightbulb.Context, error):
    # Unwrap the exception to get the original cause
    exception = error.__cause__ or error

    # codefactor tells me to do it this way instead of if elif idk 😴
    if isinstance(exception, lightbulb.NotOwner):
        return await ctx.respond(random.choice([
            "que haces goofi, no eres el libro",
            "que pesado, tu no puedes usar este comando", "tonto", "va 👍"
        ]),
                                 flags=hikari.MessageFlag.EPHEMERAL)
        # 64 -> EPHEMERAL `https://www.hikari-py.dev/hikari/messages.html#hikari.messages.MessageFlag`

    if isinstance(exception, lightbulb.CommandIsOnCooldown):
        return await ctx.respond(
            f"loco esperate unos `{exception.retry_after:.2f}` segundos, vale?",
            delete_after=10)

    if isinstance(exception, lightbulb.CommandNotFound):
        return

    if isinstance(exception, lightbulb.NotEnoughArguments):

        formatted_args = "\n".join([
            f'{e.name} :: {e.description}' for e in exception.missing_options
        ])

        return await ctx.respond(
            f"{random.choice(['espera', 'goofi', 'ehh', 'escucha,'])} te faltan argumentos 🗣️ xd\n>>> ```asciidoc\n{formatted_args}```",
            delete_after=15)

    if isinstance(exception, lightbulb.OnlyInGuild):

        return await ctx.respond(
            f"que haces en mis dms? usa los comandos en un server 😡",
            delete_after=15)

    if isinstance(exception, hikari.NotFoundError):
        return
    # elif isinstance(event.exception, lightbulb.CommandInvocationError):
    #     return

    await ctx.app.rest.create_message(
        717008102175539231,
        f"<@424213584659218445>\n```py\n{exception}```\n```py\n{error.__traceback__}```",
        user_mentions=True)

    try:
        await ctx.respond("oops, parece que algo salió mal 😨‼️")
    except:
        ...

    raise exception


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop
        uvloop.install()

    bot.run()
