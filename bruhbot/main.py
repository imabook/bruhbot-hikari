import os

import hikari
from hikari import Intents
import lightbulb

from dotenv import load_dotenv

load_dotenv()
intents = (Intents.GUILDS | Intents.GUILD_MEMBERS | Intents.GUILD_BANS
           | Intents.GUILD_EMOJIS | Intents.ALL_MESSAGES
           | Intents.GUILD_MESSAGE_REACTIONS | Intents.ALL_MESSAGE_TYPING)


def prefix(app: lightbulb.BotApp, message: hikari.Message):
    if message.author.id in [
            424213584659218445, 436521909144911874, 506565592757698600
    ]:
        return ["", "test "]
    else:
        return "test"


bot = lightbulb.BotApp(token=os.environ["TEST_TOKEN"],
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


@bot.listen(event_type=hikari.StoppingEvent)
async def on_disconnect(event: hikari.StoppingEvent):
    # se supone que se triggea justo antes de que el bot se desconecte (supongo que si discord fuerza que el bot se desconecte no avisara)
    channel = await bot.rest.fetch_channel(720392697793216642)
    await channel.send("RIP <@424213584659218445>", user_mentions=False)


@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent):

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        return
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        return await event.context.respond(
            f"Ehh esperate unos `{exception.retry_after:.2f}` segundos, vale?")
    elif isinstance(event.exception, lightbulb.CommandNotFound):
        return
    elif isinstance(event.exception, lightbulb.NotEnoughArguments):

        formatted_args = "\n".join([
            f'{e.name} :: {e.description}' for e in exception.missing_options
        ])

        return await event.context.respond(
            f"espera te faltan argumentos 🗣️ xd\n>>> ```asciidoc\n{formatted_args}```",
            delete_after=15)
    # elif isinstance(event.exception, lightbulb.CommandInvocationError):
    #     return

    raise exception


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop
        uvloop.install()

    bot.run()