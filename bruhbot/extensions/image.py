import hikari
import lightbulb

import random
import aiohttp
import io

plugin = lightbulb.Plugin("ImagePlugin")


async def _thisxdoesnotparse(ctx: lightbulb.Context, url: str, body: str):
    async with ctx.app.rest.trigger_typing(ctx.get_channel()):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                ssl=False)) as session:
            # asi no andan jodiendo los certificates (creo xd^^)
            async with session.get(
                    url, headers={'User-Agent-Forntite-Not-Goty': 'A'}) as r:

                return await ctx.respond(body,
                                         attachment=io.BytesIO(await r.read()))


@plugin.command
@lightbulb.command("persona", "Manda una foto de una persona que no existe")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def persona(ctx: lightbulb.Context):

    await _thisxdoesnotparse(ctx, "https://thispersondoesnotexist.com/image",
                             "Aqui tienes una persona NO real")

    # if isinstance(ctx.command, lightbulb.commands.SlashCommand):
    #     await response.edit(attachment=io.BytesIO(await r.read()))
    # hago este check porque el respond del slash context no usa el attachment o algo y hay que editar la foto en el mensaje
    # simplemente troleado en la siguiente version de lightbulb lo pusieron xd


@plugin.command
@lightbulb.command("gato",
                   "Manda una foto de un gato que no existe",
                   aliases=["cat"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def gato(ctx: lightbulb.Context):

    await _thisxdoesnotparse(ctx, "https://thiscatdoesnotexist.com",
                             "Aqui tienes un gato NO real")


@plugin.command
@lightbulb.command("cuadro", "Manda una foto de un cuadro que no existe")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def cuadro(ctx: lightbulb.Context):

    await _thisxdoesnotparse(ctx, "https://thisartworkdoesnotexist.com/",
                             "Aqui tienes un cuadro NO real")


@plugin.command
@lightbulb.command("waifu", "Manda una foto de una waifu 😳 que no existe")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def waifu(ctx: lightbulb.Context):

    embed = hikari.Embed(
        title="Aqui tienes una waifu 😳 NO real", color=hikari.Color(0x2f3136)
    ).set_image(
        f"https://www.thiswaifudoesnotexist.net/example-{random.randint(0, 100000)}.jpg"
    )

    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
