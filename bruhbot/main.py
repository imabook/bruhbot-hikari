import hikari
from hikari import Intents
import lightbulb

import os
from dotenv import load_dotenv

import random

from core.bot import BruhApp

load_dotenv()
intents = (Intents.GUILDS | Intents.GUILD_MEMBERS | Intents.GUILD_BANS
           | Intents.GUILD_EMOJIS | Intents.ALL_MESSAGES
           | Intents.GUILD_MESSAGE_REACTIONS | Intents.ALL_MESSAGE_TYPING)


def prefix(app: BruhApp, message: hikari.Message):
    if message.author.id in [
            424213584659218445, 436521909144911874, 506565592757698600
    ]:
        return ["", "test "]

    return "test"


bot = BruhApp(token=os.environ["TEST_TOKEN"],
              intents=intents,
              prefix=prefix,
              owner_ids=[424213584659218445, 436521909144911874],
              case_insensitive_prefix_commands=True)

[
    bot.load_extensions(f"extensions.{i[:-3]}")
    for i in os.listdir("./bruhbot/extensions/") if i.endswith(".py")
]


@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("plugin", "Plugin para cargar")
@lightbulb.command("load", "Carga el plugin especificado", hidden=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def load(ctx):
    if not ctx.options.plugin:
        return await ctx.respond("pero dime que plugin cargar no?")

    try:
        bot.load_extensions(f"extensions.{ctx.options.plugin}")
        await ctx.respond("hecho rey <:tula:748526797913849956>")
    except Exception as e:
        await ctx.respond(f"semihecho supongo xd:\n```fix\n{e}\n```")


@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("plugin", "Plugin para cargar")
@lightbulb.command("unload", "Elimina el plugin especificado", hidden=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def unload(ctx):
    if not ctx.options.plugin:
        return await ctx.respond("pero dime que plugin eliminar no?")

    try:
        bot.unload_extensions(f"extensions.{ctx.options.plugin}")
        await ctx.respond("hecho rey <:tula:748526797913849956>")
    except Exception as e:
        await ctx.respond(f"semihecho supongo xd:\n```fix\n{e}\n```")


@bot.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("reload", "Recarga todos los plugins", hidden=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def reload(ctx: lightbulb.Context):
    try:
        [
            bot.reload_extensions(f"extensions.{i[:-3]}")
            for i in os.listdir("./bruhbot/extensions/") if i.endswith(".py")
        ]
        await ctx.respond("hecho rey <:tula:748526797913849956>")
    except Exception as e:
        await ctx.respond(f"semihecho supongo xd:\n```fix\n{(e)}\n```")


@bot.listen(event_type=hikari.MessageUpdateEvent)
async def on_edit(event: hikari.MessageUpdateEvent):
    try:
        if event.message.author.is_bot:
            return
    except:
        # sometimes author is Undefined ig if its undefined it cant never be the main bot -> so actual user not bot
        pass

    try:
        ctx = await bot.get_prefix_context(event=event)
        await bot.process_prefix_commands(context=ctx)
    except Exception as e:
        print(e)

    # print(bot.get_prefix_command(
    # event.message.content))  # gotta parse the prefix out and the *args

    # try:
    #     await bot.process_prefix_commands(bot.cmdctx[event.message_id])
    # except Exception as e:
    #     print(e)


@bot.listen(event_type=hikari.StoppingEvent)
async def on_disconnect(event: hikari.StoppingEvent):
    # se supone que se triggea justo antes de que el bot se desconecte (supongo que si discord fuerza que el bot se desconecte no avisara)
    channel = await bot.rest.fetch_channel(720392697793216642)
    await channel.send("RIP <@424213584659218445>", user_mentions=False)


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent):

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    # codefactor tells me to do it this way instead of if elif idk 😴
    if isinstance(exception, lightbulb.NotOwner):
        return await event.context.respond(
            random.choice([
                "que haces goofi, no eres el libro",
                "que pesado, tu no puedes usar este comando", "tonto"
            ]))

    if isinstance(exception, lightbulb.CommandIsOnCooldown):
        return await event.context.respond(
            f"loco esperate unos `{exception.retry_after:.2f}` segundos, vale?"
        )

    if isinstance(event.exception, lightbulb.CommandNotFound):
        return

    if isinstance(event.exception, lightbulb.NotEnoughArguments):

        formatted_args = "\n".join([
            f'{e.name} :: {e.description}' for e in exception.missing_options
        ])

        return await event.context.respond(
            f"{random.choice(['espera', 'goofi', 'ehh', 'escucha,'])} te faltan argumentos 🗣️ xd\n>>> ```asciidoc\n{formatted_args}```",
            delete_after=15)
    # elif isinstance(event.exception, lightbulb.CommandInvocationError):
    #     return

    raise exception


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop
        uvloop.install()

    bot.run()