import hikari
import lightbulb

from core.embed import BetterEmbed

import random
import aiohttp
import io

plugin = lightbulb.Plugin("ImagePlugin")


async def _fetch(ctx: lightbulb.Context, url: str):
    async with ctx.app.rest.trigger_typing(ctx.get_channel()):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                ssl=False)) as session:
            # asi no andan jodiendo los certificates (creo xd^^)
            async with session.get(
                    url, headers={'User-Agent-Forntite-Not-Goty': 'A'}) as r:

                return io.BytesIO(await r.read())


@plugin.command
@lightbulb.command("persona", "Manda una foto de una persona que no existe")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def persona(ctx: lightbulb.Context):

    img = await _fetch(ctx, "https://thispersondoesnotexist.com/image")
    await ctx.respond("aqui tienes una persona NO real", attachment=img)

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

    img = await _fetch(ctx, "https://thiscatdoesnotexist.com")
    await ctx.respond("aqui tienes un gato NO real", attachment=img)


@plugin.command
@lightbulb.command("cuadro", "Manda una foto de un cuadro que no existe")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def cuadro(ctx: lightbulb.Context):

    img = await _fetch(ctx, "https://thisartworkdoesnotexist.com")
    await ctx.respond("aqui tienes un cuadro NO real", attachment=img)


@plugin.command
@lightbulb.command("waifu", "Manda una foto de una waifu 😳 que no existe")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def waifu(ctx: lightbulb.Context):

    embed = BetterEmbed(title="aqui tienes una waifu 😳 NO real").set_image(
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
    color = ctx.options.codigo

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

    embed = BetterEmbed(
        color=color_hex,
        title=f"{js['name']['value']}",
        description=
        f"Colorcode: **#{color_hex}**\nEl código en base 10 sería: **{int(color, 16)}**\n Su valor en RGB: r: **{js['rgb']['r']}** g: **{js['rgb']['g']}** b: **{js['rgb']['b']}**"
    ).set_image(
        f"http://singlecolorimage.com/get/{color_hex}/300x120").set_thumbnail(
            f"http://singlecolorimage.com/get/{color_hex}/100x100").set_footer(
                "Para más info puedes ir a https://htmlcolorcodes.com/ 😎")

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.option("texto",
                  "El texto que quieres que se convierta en QR",
                  modifier=lightbulb.commands.OptionModifier.CONSUME_REST,
                  required=True)
@lightbulb.command("qr", "Crea un QR con el texto que tu quieras")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def qr(ctx: lightbulb.Context):

    img = await _fetch(
        ctx,
        f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={ctx.options.texto.replace(' ', '+')}"
    )
    embed = BetterEmbed(
        title="aqui tienes tu qr supongo",
        description=f"su contenido es `{ctx.options.texto}` 👍").set_image(img)

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.option(
    "member",
    "El miembro que quieras elegir",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
    type=hikari.Member,  # lightbulb.MemberConverter should also work
    required=False)
@lightbulb.command("avatar", "Muestra el avatar de un usuario")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def avatar(ctx: lightbulb.Context):
    member = ctx.options.member

    if not member:
        member = ctx.member

    embed = BetterEmbed(
        title=f"esta es la foto de perfil de {member.username}",
        color=member.get_top_role().color
    ).set_image(member.avatar_url or member.default_avatar_url).set_footer(
        random.choice([
            "no te voy a mentir pero se le ve bastante fresco 😳",
            "are you winning son?", "willyrex lo aprueba 😎",
            "vegeta777 no lo aprueba 😔",
            f"menuda foto de perfil de jugador de freefire tiene el {member.username} este 🗿",
            "que", "esta bastante bien pero no es mejor que la mía 🤑",
            "eso no es el juego fortnite de epic games fornite©️?", "ido"
        ]))

    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
