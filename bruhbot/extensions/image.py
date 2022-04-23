import hikari
import lightbulb

from core.embed import BetterEmbed

import random
import aiohttp
import io

import PIL.ImageOps as PIO
from PIL import Image as Img
from PIL import ImageFilter, ImageFont, ImageDraw

plugin = lightbulb.Plugin("ImagePlugin")


async def _fetch(ctx: lightbulb.Context, url: str):
    async with ctx.app.rest.trigger_typing(ctx.get_channel()):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                ssl=False)) as session:
            # asi no andan jodiendo los certificates (creo xd^^)
            async with session.get(
                    url, headers={'User-Agent-Forntite-Not-Goty': 'A'}) as r:

                return io.BytesIO(await r.read())


def _img_to_bytes(img):
    #  god bless https://stackoverflow.com/a/33117447/12595762
    byte_array = io.BytesIO()
    img.save(byte_array, format="PNG")

    return byte_array.getvalue()


def _blend(avatar, image, opacity=70):
    avatar = avatar.resize((324, 324)).convert("RGBA")
    img = Img.open(f"./bruhbot/assets/images/{image}").resize(
        (324, 324)).convert("RGBA")
    img.putalpha(opacity)
    avatar.paste(img, (0, 0), img)

    return _img_to_bytes(avatar)


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
    type=hikari.Member,
    required=False,
)
@lightbulb.command("avatar", "Muestra el avatar de un usuario")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def avatar(ctx: lightbulb.Context):

    member = ctx.options.member or ctx.member

    color = None

    if isinstance(member, hikari.Member):
        color = member.get_top_role().color

    embed = BetterEmbed(
        title=f"esta es la foto de perfil de {member.username}", color=color
    ).set_image(member.avatar_url or member.default_avatar_url).set_footer(
        random.choice([
            "no te voy a mentir pero se le ve bastante fresco 😳",
            "are you winning son?", "willyrex lo aprueba 😎",
            "vegeta777 no lo aprueba 😔",
            f"menuda foto de perfil de jugador de freefire tiene el {member.username} este 🗿",
            "que", "esta bastante bien pero no es mejor que la mía 🤑",
            "free fire?", "ido"
        ]))

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.option(
    "member",
    "El miembro que quieras invertir",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
    type=hikari.User,
    required=False,
)
@lightbulb.command("invert",
                   "Invierte los colores de la foto de perfil de alguien")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def invert(ctx: lightbulb.Context):

    member = ctx.options.member or ctx.member

    byte_array = await _fetch(
        ctx, member.avatar_url.url
        if member.avatar_url else member.default_avatar_url.url)
    img = PIO.invert(Img.open(byte_array).convert("RGB"))

    byte_array = _img_to_bytes(img)

    await ctx.respond(random.choice(
        ["🙃 ɐᴉpǝɯoɔ ɐɾɐɾ", "ɾɐɾɐ ɔoɯǝpᴉɐ 🙃", "🙂 aidemoc ajaj"]),
                      attachment=byte_array)


@plugin.command
@lightbulb.option(
    "member",
    "El miembro que quieras elegir",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
    type=hikari.User,
    required=False,
)
@lightbulb.command("español",
                   "Dice como de española es una persona",
                   aliases=["españa"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def spanish(ctx: lightbulb.Context):

    member = ctx.options.member or ctx.member

    byte_array = await _fetch(
        ctx, member.avatar_url.url
        if member.avatar_url else member.default_avatar_url.url)

    byte_array = _blend(Img.open(byte_array), "españa.png")

    meter = random.randint(0, 100)
    if meter == 0:
        text = f"ayy pa, **0%** de español, eres un alto peruano {member.name} 🐒"
    elif meter <= 25:
        text = f"es poquito pero eres **{meter}%** español, sigue así 😎"
    elif meter <= 75:
        text = f"eh eh eh eh, que tener un **{meter}%** de español no esta nada mal, no te desanimes 🧐"
    elif meter <= 99:
        text = f"papurri estas loco papurri, tremendo español **{meter}%** que tenemos aqui, estas l0co 🤑"
    else:
        # meter == 100
        text = f"lo veo y no lo creo 😳😳😳, eres **100%** español!!111!1"

    await ctx.respond(text, attachment=byte_array)


@plugin.command
@lightbulb.option(
    "member",
    "El miembro que quieras elegir",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
    type=hikari.User,
    required=False,
)
@lightbulb.command("gay", "Dice como de gay es una persona")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def gay(ctx: lightbulb.Context):

    member = ctx.options.member or ctx.member

    byte_array = await _fetch(
        ctx, member.avatar_url.url
        if member.avatar_url else member.default_avatar_url.url)

    byte_array = _blend(Img.open(byte_array), "gay.png")

    meter = random.randint(0, 100)
    if meter == 0:
        text = f"esto si que es totalmente epico, estoy notando un **0%** de gay, enhorabuena {member.name}"
    elif meter <= 25:
        text = f"es poquito pero te he diagnosticado con el gay, tienes un **{meter}%**"
    elif meter <= 75:
        text = f"**{meter}%** de gay ⚠️"
    elif meter <= 99:
        text = f"dios **{meter}%** de gay, eso es mucho más de uno"
    else:
        text = f"no puede ser 😳😳😳 **100%** gay"

    await ctx.respond(text, attachment=byte_array)


@plugin.command
@lightbulb.option(
    "member",
    "El miembro que quieras elegir",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
    type=hikari.User,
    required=False,
)
@lightbulb.command("comunista",
                   "Dice como de comunista es una persona",
                   aliases=["comunismo"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def communism(ctx: lightbulb.Context):

    member = ctx.options.member or ctx.member

    byte_array = await _fetch(
        ctx, member.avatar_url.url
        if member.avatar_url else member.default_avatar_url.url)

    byte_array = _blend(Img.open(byte_array), "comunismo.png")

    meter = random.randint(0, 100)
    if meter == 0:
        text = f"simplemente 0%"
    elif meter <= 25:
        text = f"top **{meter}%** de comunismo"
    elif meter <= 75:
        text = f"china cuando **{meter}%** de comunismo"
    elif meter <= 99:
        text = f"**{meter}%** 😈😈"
    else:
        # meter == 100
        text = f"finalmente 100% de comunismo"

    await ctx.respond(text, attachment=byte_array)


@plugin.command
@lightbulb.option(
    "member",
    "El miembro que quieras pixelar",
    modifier=lightbulb.OptionModifier.CONSUME_REST,
    type=hikari.User,
    required=False,
)
@lightbulb.command("pixelar", "Pixela a una persona", aliases=["censurar"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def pixelar(ctx: lightbulb.Context):

    member = ctx.options.member or ctx.member

    byte_array = await _fetch(
        ctx, member.avatar_url.url
        if member.avatar_url else member.default_avatar_url.url)

    img = Img.open(byte_array)
    imgs = img.resize((16, 16), resample=Img.BILINEAR)
    # (img.size) a (256, 256) porque creo que se ve mejor asi
    imgs = imgs.resize((256, 256), Img.NEAREST)

    byte_array = _img_to_bytes(imgs)

    await ctx.respond(random.choice(
        ["explicit", "█████ de ████    ███████", "🥶"]),
                      attachment=byte_array)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
