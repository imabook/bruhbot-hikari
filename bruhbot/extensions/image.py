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
                             "aqui tienes una persona NO real")

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
                             "aqui tienes un gato NO real")


@plugin.command
@lightbulb.command("cuadro", "Manda una foto de un cuadro que no existe")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def cuadro(ctx: lightbulb.Context):

    await _thisxdoesnotparse(ctx, "https://thisartworkdoesnotexist.com/",
                             "aqui tienes un cuadro NO real")


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


@plugin.command
@lightbulb.option("codigo", "El valor del color en base 16", required=False)
@lightbulb.command("color",
                   "Te manda el color a partir de su hexcode",
                   aliases=["colorcode"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def color(ctx: lightbulb.Context):
    # metodo un poco peruano
    color = ctx.options.code

    if not color:
        color = hex(random.randint(0x000000, 0xFFFFFF)).replace("0x", "")
    elif color.startswith("0x"):
        if len(color) > 8:
            await ctx.respond("te pasas bro :flushed:", delete_after=5)
            return
    elif color.startswith("#"):
        if len(color) > 7:
            await ctx.respond("te pasas bro :flushed:", delete_after=5)
            return
    else:
        if len(color) > 6:
            await ctx.respond("te pasas bro :flushed:", delete_after=5)
            return

    if type(color) == str:
        try:
            color = color.strip("#")
            color = color.replace("0x", "")
            color = hex(int(color, 16)).replace("0x", "")
        except Exception:
            await ctx.respond(
                f"loco el código `{color}` no esta bien escrito :flushed: si quieres ver como se pondrian los colorcodes checkea esta página <https://htmlcolorcodes.com/> :sunglasses: ",
                delete_after=7)
            return

    color_hex = color
    while len(color_hex) != 6:
        # rellenando 0 donde no hay: 0xFF -> 0x0000FF
        color_hex = "0" + color_hex

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
            ssl=False)) as session:
        async with session.get(
                f'https://www.thecolorapi.com/id?format=json&hex={color_hex}'
        ) as r:
            js = await r.json()

    embed = hikari.Embed(
        color=color_hex,
        title=f"{js['name']['value']}",
        description=
        f"Colorcode: **#{color_hex}**\nEl código en base 10 sería: **{int(color, 16)}**\n Su valor en RGB: r: **{js['rgb']['r']}** g: **{js['rgb']['g']}** b: **{js['rgb']['b']}**"
    ).set_image(
        f"http://singlecolorimage.com/get/{color_hex}/300x120").set_thumbnail(
            f"http://singlecolorimage.com/get/{color_hex}/100x100").set_footer(
                "Para más info puedes ir a https://htmlcolorcodes.com/ 😎")

    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
