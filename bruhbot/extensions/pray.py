import lightbulb
import hikari
import miru

from lightbulb.ext import tasks

import random
import math
import asyncio

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from lightbulb.utils import nav
from core.bot import BruhApp

from database.db_handler import *
from utils.items import *
from core.embed import BetterEmbed
from utils import views
from utils.views import get_price
from utils.blackjack import *
from utils.misiones import handle_mission_progression

plugin = lightbulb.Plugin("Economía")
plugin.add_checks(lightbulb.guild_only)

# xd
PALABRAS_FEAS = [
    "cabrón", "hdp", "mmg", "inútil", "botardo", "npc", "mamabicho"
]


async def callback(ctx: lightbulb.Context):
    amuletos = await ctx.bot.db.fetch_amuletos(ctx.author.id) or 0

    return lightbulb.UserBucket(120 - 5 * amuletos, 1)


def get_utc() -> datetime:
    return datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))


def get_timestamp(d: datetime) -> int:
    """ Converts utc to utc+2 and gets the timestamp """

    # i know all timestamps are the same without minding timezone but it has to work like this, all dates displayed on spain timezone not utc

    # gotta change hours to 0, when the bot is in the server you dont need to add hours for the timestamp to be correct

    return round((d + timedelta(hours=0)).timestamp())


def human_format(num):
    # si lo he sacado de stack overflow porque no me sale de los huevos hacer esto yo mismo
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                         ['', 'K', 'M', 'B', 'T'][magnitude])


@plugin.command
@lightbulb.add_cooldown(callback=callback)
@lightbulb.command("pray", "Reza para conseguir praycoins", aliases=["p"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pray(ctx: lightbulb.Context):

    new_user = False
    amuletos = await ctx.bot.db.fetch_amuletos(ctx.author.id)

    if amuletos == None:
        new_user = True

        # i hate timezones and dates on god 😩
        # all timezones are saved in utc (spain/madrid timezone is utc+2 -> ZoneInfo('Europe/Madrid'))

        await ctx.bot.db.register_user(ctx.author.id, get_utc())
        amuletos = 0

    coins = await ctx.bot.db.fetch_coins(ctx.author.id)

    await ctx.bot.db.update_coins(ctx.author.id, coins + 1 + amuletos)
    await ctx.bot.db.update_prays(ctx.author.id)

    if new_user:
        await ctx.respond(
            f"buenas {ctx.author.mention}, eres nuevo y tal y probablemente quieras leer todo esto\nah y tu religión no tiene nombre todavía, usa el comando `religion` para ponerle uno",
            embed=BetterEmbed(
                title="Mira, estos son algunos comandos que puedes usar",
                color=(await ctx.member.fetch_roles())[-1].color).
            add_field(
                name="`pray`",
                value=
                "Rezas y consigues una praycoin <:praycoin:758747635909132387>, al principio solo puedes rezar cada dos minutos"
            ).add_field(
                name="`pinfo`",
                value=
                "Ves cuantas praycoins <:praycoin:758747635909132387> tienes y las cosas que has comprado"
            ).add_field(
                name="`shop`",
                value=
                "La tienda rey, para ver que puedes comprar con tus praycoins <:praycoin:758747635909132387>"
            ).add_field(
                name="Y pues eso",
                value=
                "Hay mas cosas, para verlas haz /help pero ahora a rezar 😎🙏"),
            user_mentions=False)
        return

    await ctx.respond(
        f"ahora tienes **{(coins + 1 + amuletos):,}** <:praycoin:758747635909132387>"
        .replace(",", ".") +
        f", {random.choice(['sigue asi', 'dale', 'durisimo', 'bendecido'])} {random.choice(['🤑', '😎🙏', '😇'])}"
    )

    await ctx.bot.db.handle_xp(ctx, ctx.author.id)
    await handle_mission_progression(ctx, 1, 1)
    await handle_mission_progression(ctx, 2, 1)

    await handle_mission_progression(ctx, 9, 1 + amuletos)


@plugin.command
@lightbulb.add_cooldown(length=10, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option("miembro",
                  "El miembro que quieras elegir",
                  type=hikari.Member,
                  required=False)
@lightbulb.command("pinfo",
                   "Te muestra información sobre religiones",
                   aliases=["prayinfo"])
@lightbulb.implements(lightbulb.SlashCommand)
async def pinfo(ctx: lightbulb.Context):
    member = ctx.options.miembro or ctx.member

    data = await ctx.bot.db.fetch_prayinfo(member.id)

    if not data[0] or not data[1]:
        # user isnt in the db
        await ctx.respond(
            f"cabrón, por qué quieres saber cosas de {member.mention} si se ve que no ha rezado ni una sola vez?",
            user_mentions=False,
            delete_after=10)
        return

    lvl, _ = await ctx.bot.db.fetch_level(member.id)

    # user_info // economy_info
    ui, ei = data

    pph = ei[1] * (ei[2] + 1) + ei[4] * 10 * (ei[5] + 1)

    await ctx.respond(embed=BetterEmbed(
        title=ui[0] or f"La religión de {member.username}", color=0xFCA51F
    ).add_field(
        name="Praycoins:",
        value=
        f"{member.mention} tiene **{ei[0]}** <:praycoin:758747635909132387> y es nivel **{lvl}**\nHa rezado **{ui[1]}** veces y empezó <t:{get_timestamp(ui[2])}:R> 😨\nConsigue **{pph}** <:praycoin:758747635909132387> por hora 🤑\nHa recibido **{ui[3]}** <:praycoin:758747635909132387> y ha dado **{ui[4]}** <:praycoin:758747635909132387>"
    ).add_field(
        name="Cosas compradas:",
        value=
        f"Hay **{ei[1]} ** abuelas que creen en su religión\nSe han construido **{ei[2]}** iglesias\nUnos **{ei[4]}** guiris visitan las iglesias\nHay **{ei[5]}** máquinas de donaciones en cada iglesia para que los guiris suelten los cheles 🤑\nEn total hay **{ei[6]}** ángeles ayudando a su religión\nY tiene mejorado **{ei[3]}** veces el amuleto"
    ).set_footer(
        text="eh mi loco, has probado ya el '/pcard' ?").set_thumbnail(
            member.avatar_url or member.default_avatar_url))


@plugin.command
@lightbulb.add_cooldown(length=15, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option("miembro",
                  "El miembro que quieras elegir",
                  type=hikari.Member,
                  required=True)
@lightbulb.option("cantidad",
                  "Cantidad de monedas que quieres dar",
                  type=str,
                  required=True)
@lightbulb.command("give", "Das monedas a la persona que quieras")
@lightbulb.implements(lightbulb.SlashCommand)
async def give(ctx: lightbulb.Context):
    if ctx.options.miembro.is_bot:
        await ctx.respond(
            "a un bot?\nen serio quieres darle monedas a un bot?",
            delete_after=10)
        return

    if ctx.options.miembro.id == ctx.member.id:
        await ctx.respond(random.choice([
            "no", "autodonacion?", "espera que ahora se las doy...", "🗿",
            "real?"
        ]),
                          delete_after=10)
        return

    author_coins = await ctx.bot.db.fetch_coins(ctx.member.id)

    if ctx.options.cantidad == "all":
        amount = author_coins
    else:
        try:
            amount = int(ctx.options.cantidad)
        except ValueError:
            await ctx.respond(
                f"dame un número entero, no \"**{ctx.options.cantidad}**\"",
                user_mentions=False,
                role_mentions=False,
                mentions_everyone=False,
                delete_after=10)
            return

    if amount <= 0:
        await ctx.respond(
            f"**{amount}** <:praycoin:758747635909132387> ehh \nalto gracioso 🗿",
            delete_after=10)
        return

    if not author_coins or author_coins < amount:
        await ctx.respond(
            f"te crees que las monedas se hacen solas?\ntienes **{author_coins or 0}** praycoins 🗿, regala menos monedas o sé menos humilde 🐠",
            delete_after=10)

        return

    other_coins = await ctx.bot.db.fetch_coins(ctx.options.miembro.id)

    if other_coins == None:
        await ctx.respond(
            f"el chaval no ha rezado ni una sola vez, deja que se haga una religión o lo que sea antes",
            delete_after=10)

        return

    # await update_coins(ctx.bot.mysql, ctx.member.id,
    #                    author_coins - ctx.options.amount)
    # await update_coins(ctx.bot.mysql, ctx.options.member.id,
    #                    other_coins + ctx.options.amount)

    await ctx.bot.db.make_transaction(ctx.member.id, ctx.options.miembro.id,
                                      author_coins, other_coins, amount)

    # actually yucky formatting
    await ctx.respond(
        BetterEmbed(
            description=
            f"{ctx.member.mention} le ha dado **{amount}** a {ctx.options.miembro.mention}"
        ).add_field(name=ctx.member.username,
                    value=f"```py\nPraycoins: {author_coins - amount}\n```",
                    inline=True).add_field(
                        name=ctx.options.miembro.username,
                        value=f"```py\nPraycoins: {other_coins + amount}\n```",
                        inline=True))

    await handle_mission_progression(ctx, 8, amount)


@plugin.command
@lightbulb.add_cooldown(length=15, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option(
    "nombre",
    "El nuevo nombre que quieres ponerle a tu religión",
    type=str,
    modifier=lightbulb.OptionModifier.CONSUME_REST,
    required=False,
)
@lightbulb.command("religion", "Cambias el nombre a tu religión")
@lightbulb.implements(lightbulb.SlashCommand)
async def religion(ctx: lightbulb.Context):
    religion = await ctx.bot.db.fetch_religion(ctx.member.id)

    if not await ctx.bot.db.validate_user(ctx.author.id):
        await ctx.respond(
            "si quieres ponerle un nombre a tu religión, reza primero anda",
            delete_after=10)
        return

    if not ctx.options.nombre:
        if religion:
            await ctx.respond(
                f"tu religion se llama **{religion}**, bastante duro la verdad"
            )
        else:
            await ctx.respond(
                f"todavia no tienes ningún nombre puesto para tu religión")
        return

    name = ctx.options.nombre[:25]

    await ctx.bot.db.update_religion(ctx.member.id, name)

    if len(ctx.options.nombre) > 25:
        await ctx.respond(
            f"**{ctx.options.nombre}**...\nno rey eso es muy largo, le voy a poner **{name}** de nombre\nsi no te gusta pues piensa otro mejor porque tienes 15s de cooldown 👿",
            mentions_everyone=False,
            role_mentions=False,
            user_mentions=False)
        return

    await ctx.respond(
        f"**{name}**, real? está bien\na partir de ahora así se llamará tu religión",
        mentions_everyone=False,
        role_mentions=False,
        user_mentions=False)


@plugin.command
@lightbulb.add_cooldown(length=15, uses=1, bucket=lightbulb.GuildBucket)
@lightbulb.option(
    "tipo",
    "Cambia el tipo de estadística",
    choices=["praycoins", "donaciones", "recibidas", "oraciones", "nivel"],
    default="praycoins",
    required=False,
)
@lightbulb.option(
    "alcance",
    "El tipo de alcance, global/server",
    choices=["global", "server"],
    default="global",
    required=False,
)
@lightbulb.command("ranks", "Te muestra un ranking de las mejores religiones")
@lightbulb.implements(lightbulb.SlashCommand)
async def ranks(ctx: lightbulb.Context):

    changes = {
        "praycoins": "coins",
        "donaciones": "given",
        "recibidas": "recieved",
        "oraciones": "prayed",
        "nivel": "lvl"
    }
    value_changes = {
        "praycoins": "<:praycoin:758747635909132387> praycoins 🤑",
        "donaciones": "<:praycoin:758747635909132387> donadas 😊",
        "recibidas": "<:praycoin:758747635909132387> recibidas 😇",
        "oraciones": "veces rezadas 🙏",
        "nivel": " niveles"
    }
    title_changes = {
        "praycoins": "religiosas",
        "donaciones": "humildes",
        "recibidas": "mendigas",
        "oraciones": "dedicadas",
        "nivel": "dedicadas"
    }

    if ctx.options.tipo == "praycoins":
        QUERY = "SELECT id, coins FROM economy WHERE id IN %s ORDER BY coins DESC;"
    else:
        QUERY = f"SELECT id, {changes[ctx.options.tipo]} FROM users WHERE id IN %s ORDER BY {changes[ctx.options.tipo]} DESC;"

    embed = BetterEmbed(
        title=
        f"Las personas más {title_changes[ctx.options.tipo]} de{' ' + ctx.get_guild().name if ctx.options.alcance == 'server' else 'l mundo'}",
        color=0xFCA51F)

    # puede que la mejor forma de hacer esto sea pillar TODAS las ids de la base de datos e interpolarlas con las ids de los miembros del server
    # userslist = set(userslist) & set(members)
    # ese es el codigo viejo viejo del dpy, pero vamos que maxeaba el cpu y tal asique puede que no sea la mejor forma xd

    cached_ids = {}
    if ctx.options.alcance and ctx.options.alcance == "server":

        embed.set_thumbnail(ctx.get_guild().icon_url)

        ids = []
        async for m in ctx.bot.rest.fetch_members(ctx.guild_id):
            ids.append(int(m.id))
            cached_ids[int(m.id)] = m.username

        ids = tuple(ids)

        # data = await ctx.bot.mysql.fetchmany(
        #     10, "SELECT id, %s FROM economy WHERE id IN %s ORDER BY %s DESC;",
        #     (changes[ctx.options.type], ids, changes[ctx.options.type]))

        data = await ctx.bot.mysql.fetchmany(10, QUERY, (ids, ))

    else:
        data = await ctx.bot.mysql.fetchmany(
            10, QUERY.replace("WHERE id IN %s ", ""))

    if cached_ids:
        [
            embed.add_field(
                name=f"#{x + 1} - {cached_ids[d[0]]}",
                value=f"Con {d[1]:,} {value_changes[ctx.options.tipo]}".
                replace(",", ".")) for x, d in enumerate(data)
        ]
    else:
        # si la cuenta ha sido borrada (id y todo) y sigue en la base de datos va a dar error (arreglar si eso)
        # no da error pero se presenta como Deleted User #....
        [
            embed.add_field(
                name=
                f"#{x + 1} - {ctx.get_guild().get_member(d[0]).username if ctx.get_guild().get_member(d[0]) else (await ctx.bot.rest.fetch_user(d[0])).username}",
                value=f"Con **{d[1]:,}** {value_changes[ctx.options.tipo]}".
                replace(",", ".")) for x, d in enumerate(data)
        ]

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.add_cooldown(length=10, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option("miembro",
                  "El miembro que quieras elegir",
                  type=hikari.Member,
                  required=False)
@lightbulb.command("level",
                   "Te muestra tu nivel o el de otros",
                   aliases=["lvl"])
@lightbulb.implements(lightbulb.SlashCommand)
async def level(ctx: lightbulb.Context):
    member = ctx.options.miembro or ctx.member

    if not await ctx.bot.db.validate_user(member.id):
        await ctx.respond(
            f"loco, por qué quieres ver el nivel de {member.mention} si se ve que no ha rezado nunca?"
            if ctx.options.miembro else
            "si quieres ver tu nivel y tal, reza primero anda",
            delete_after=10,
            user_mentions=False)
        return

    # cambiar el output y tal -> usar una foto a lo mejor con las barras
    lvl, xp = await ctx.bot.db.fetch_level(member.id)
    max = ctx.bot.db.get_max_xp(lvl)

    # uncomment this out when you implement top.gg
    view = miru.View(timeout=0)
    view.add_item(
        miru.Button(style=hikari.ButtonStyle.LINK,
                    label="vota y consigue 20% más de xp " +
                    random.choice(["‼️", "👍", "🦍", ""]),
                    url="https://top.gg/bot/693163993841270876/vote"))

    await ctx.respond(
        f"{member.mention} es nivel **{lvl}**\n{xp}/{max} necesita **{max - xp}** de xp para subir de nivel"
        if ctx.options.miembro else
        f"eres nivel **{lvl}**\n**{xp}/{max}** necesitas **{max - xp}** de xp para subir de nivel",
        user_mentions=False,
        components=view)


@plugin.command
@lightbulb.add_cooldown(length=10, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.command("shop", "Te muestra la tienda", aliases=["tienda"])
@lightbulb.implements(lightbulb.SlashCommand)
async def shop(ctx: lightbulb.Context):
    if not await ctx.bot.db.validate_user(ctx.author.id):
        await ctx.respond(
            "si quieres ver la tienda y los precios, reza primero anda",
            delete_after=10)
        return

    lvl = await ctx.bot.db.fetch_level_only(ctx.member.id)
    shop_info = await ctx.bot.db.fetch_shop()
    user_shop = await ctx.bot.db.fetch_user_shop(ctx.author.id)

    desc = f"**Abuela** -> **{get_price(user_shop[1] + 1, 'abuelas'):,}** <:praycoin:758747635909132387>\nConsigues una moneda por hora\n`hay {shop_info[0]:,} abuelas totales creyendo en diferentes religiones`\n**Iglesia** -> **{get_price(user_shop[2] + 1, 'iglesias'):,}** <:praycoin:758747635909132387>\nTodas las abuelas generan una moneda más por hora\n`se han construido {shop_info[1]:,} iglesias en total`\n**Amuleto religioso** -> **{get_price(user_shop[3] + 1, 'amuletos'):,}** <:praycoin:758747635909132387>\nConsigues una moneda más al rezar y se reduce el tiempo de espera por 5s\n`solo se pueden tener 15 por persona`\n"

    if lvl >= 10:
        desc += f"**Ángel** -> **{get_price(user_shop[6] + 1, 'angeles'):,}** <:praycoin:758747635909132387>\nCada ángel te da 10.000 monedas cada día y aumenta tus ganancias de xp\n`hay {shop_info[4]:,} ángeles ayudando distintas religiones en total`\n"

        if lvl >= 15:
            desc += f"**Guiri** -> **{get_price(user_shop[4] + 1, 'guiris'):,}** <:praycoin:758747635909132387>\nConsigues 10 monedas por hora\n`hay {shop_info[2]:,} guiris visitando religiones en el mundo`\n"

            if user_shop[4] > 0:
                desc += f"**Máquina de donaciones** -> **{get_price(user_shop[5] + 1, 'donaciones'):,}** <:praycoin:758747635909132387>\nCada guiri se deja 10 monedas más por cada máquina\n`hay {shop_info[3]:,} máquinas de donaciones totales`"

    embed = BetterEmbed(
        title="Tienda",
        description=
        f"Para ir desbloqueando nuevas cosas para comprar tendras que subir de nivel\nEres nivel **{lvl}** y tienes **{user_shop[0]}** <:praycoin:758747635909132387>\n\n{desc}"
        .replace(",", "."),
        color=0x30A8FF)

    await ctx.respond(embed=embed)


@plugin.command
@lightbulb.add_cooldown(length=15, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.command("buy", "Compras el objeto que quieras de la tienda")
@lightbulb.implements(lightbulb.SlashCommand)
async def buy(ctx: lightbulb.Context):
    if not await ctx.bot.db.validate_user(ctx.author.id):
        await ctx.respond(
            "si quieres consumir y comprar algo, reza primero anda",
            delete_after=10)
        return

    options = [
        "Abuelas", "Iglesias", "Amuletos", "Ángeles", "Guiris",
        "Máquinas de donaciones"
    ]

    # checking if they have the level necessary to buy that object
    lvl = await ctx.bot.db.fetch_level_only(ctx.member.id)

    if lvl >= 10:
        if lvl >= 15:
            if await ctx.bot.mysql.fetchone(
                    "SELECT guiris FROM economy WHERE id = %s",
                (ctx.author.id, )) == 0:
                options = options[:-1]
        else:
            options = options[:-2]
    else:
        options = options[:-3]

    view = views.BuyView(timeout=45, author_id=ctx.author.id)
    view.add_item(views.SelectObjectButton(options))
    # view.add_item(views.SelectAmountButton(disabled=True))

    message = await ctx.respond("que es lo que quieres comprar rey?",
                                components=view)
    await view.start(message)
    await view.wait()  # wait for it to end or time out

    if view.bought:
        await ctx.bot.db.handle_xp(ctx, ctx.author.id, view.bonus)


@plugin.command
@lightbulb.add_cooldown(length=15, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.command("daily", "Reclama recompensas diarias")
@lightbulb.implements(lightbulb.SlashCommand)
async def daily(ctx: lightbulb.Context):
    if not await ctx.bot.db.validate_user(ctx.author.id):
        await ctx.respond("si quieres hacer este comando, reza primero anda",
                          delete_after=10)
        return

    timeout = await ctx.bot.db.get_timeout(ctx.author.id)

    if timeout != 0:
        await ctx.respond(
            f"no ha pasado un día todavía rey 👿\npodrás hacer el comando <t:{math.ceil((datetime.utcnow() + timedelta(hours=0, seconds=timeout)).timestamp())}:R>"
        )
        return

    # if True:
    if random.randint(0, 3) == 0:
        # tier 1 -> 50% normal
        # tier 2 -> 20% duro
        # tier 3 -> 15% epico
        # tier 4 -> 10% legendario
        # tier 5 -> 5% GALACTICO
        # tier 0 -> 0% (patreon shit etc)
        items = []
        i = random.randint(0, 99)

        tier = 5

        if i < 50:
            tier = 1
        elif 50 <= i and i < 70:
            tier = 2
        elif 70 <= i and i < 85:
            tier = 3
        elif 85 <= i and i < 95:
            tier = 4

        items = await ctx.bot.db.fetch_item_from_tier(tier)

        # i = fetch_user_item(ctx.bot.mysql, item, ctx.author.id)
        # if i == None:
        #     await store_item(ctx.bot.mysql, ctx.author.id, item)
        # else:
        #     await update_items_add(ctx.bot.mysql, ctx.author.id, item)

        item = random.choice(items)

        await ctx.bot.db.update_user_items(ctx.author.id, item[0], "add")

        # TODO: cambiar el mensaje dependiendo del TIER !!

        await ctx.respond(
            f"nuevo día ehh? has conseguido un item\n{item[1]['emoji']} **{item[1]['name']}**: {item[1]['description']}"
        )
        return

    # gracias marc 🙏

    ei = await ctx.bot.db.fetch_user_shop(ctx.author.id)
    pph = ei[1] * (ei[2] + 1) + ei[4] * 10 * (ei[5] + 1)

    # para que la gente del principio consiga monedas
    if pph < 5:
        coins = random.randint(5, 50)
    else:
        coins = random.randint(pph, pph * 12)
    # El maximo de prays que se podrán conseguir serán pues worth x horas y el minimo 1 hora, asi sirve de algo el daily cuando subes un poco de nivel
    await ctx.bot.db.update_coins_add(ctx.author.id, coins)

    await ctx.respond(
        f"nuevo día ehh? has conseguido **{coins}** <:praycoin:758747635909132387>\na ver si mañana consigues un item"
    )

    await handle_mission_progression(ctx, 9, coins)


@plugin.command
@lightbulb.add_cooldown(length=10, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.command("use", "Usa un item que tengas")
@lightbulb.implements(lightbulb.SlashCommand)
async def use(ctx: lightbulb.Context):
    user_items = await ctx.bot.db.fetch_user_items(ctx.author.id)

    ids = tuple(i[0] for i in user_items)
    user_items = {i[0]: i[1] for i in user_items}

    if not user_items:
        await ctx.respond("no tienes ningún item")
        return

    items = {
        i[0]: [i[1], i[2], i[3], user_items[i[0]]]
        for i in await ctx.bot.db.fetch_item_info(ids)
    }

    # {id: [name, desc, emoji, usos...], ...}
    view = views.UseItemView(timeout=60, items=items, author_id=ctx.author.id)

    message = await ctx.respond(
        f"tienes **{len(user_items)}** items\ncual de ellos quieres usar?",
        components=view)

    await view.start(message)


@plugin.command
@lightbulb.add_cooldown(length=15, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.command("misiones", "Mira las misiones que tienes")
@lightbulb.implements(lightbulb.SlashCommand)
async def misiones(ctx: lightbulb.Context):
    lvl = await ctx.bot.db.fetch_level_only(ctx.author.id)

    if not lvl or lvl < 5:
        # no tiene misiones todavia
        await ctx.respond(
            "cuando subas de nivel conseguiras más misiones:\n- [vota al bot](<https://top.gg/bot/693163993841270876/vote>) | x1 item"
        )

        return

    user_missions = await ctx.bot.db.fetch_user_missions(ctx.author.id)

    if not user_missions:
        await ctx.respond(
            "- [vota al bot](<https://top.gg/bot/693163993841270876/vote>) | x1 item"
        )
        return

    mission_info = await ctx.bot.db.fetch_mission_info(
        tuple([i[0] for i in user_missions]))

    # pablo m3 m4 referencia !!! ..__.:.!!!
    # OMG simplemente confia
    comp = [(
        f"- {mission_info[m[0]]} **{m[3]}/{m[4]} ({round(m[3] * 100/m[4])}%)**, se resetea <t:{get_timestamp(m[1])}:R> | "
        + (f"{m[2]:,} <:praycoin:758747635909132387>"
           if m[2] != 0 else "x1 item")
    ) if m[3] != m[4] else (
        f"- ~~{mission_info[m[0]]} **{m[3]}/{m[4]} ({round(m[3] * 100/m[4])}%)**, se resetea <t:{get_timestamp(m[1])}:R> | "
        + (f"{m[2]:,} <:praycoin:758747635909132387>~~"
           if m[2] != 0 else "x1 item~~")) for m in user_missions]

    await ctx.respond(
        "\n".join(comp).replace(",", ".") +
        "\n\n- [vota al bot](<https://top.gg/bot/693163993841270876/vote>) | x1 item"
    )


@plugin.command
@lightbulb.add_cooldown(length=5, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option("cantidad",
                  "La cantidad de dinero que quieres apostar",
                  type=str,
                  required=True)
@lightbulb.command("gamble", "Apuesta dinero y reza para no perderlo")
@lightbulb.implements(lightbulb.SlashCommand)
async def gamble(ctx: lightbulb.Context):
    # checking and stuff
    coins = await ctx.bot.db.fetch_coins(ctx.author.id)

    if coins == None:
        await ctx.respond("si quieres apostar praycoins, reza primero anda",
                          delete_after=10)
        return

    if ctx.options.cantidad == "all":
        amount = coins
    else:
        try:
            amount = int(ctx.options.cantidad)
        except ValueError:
            await ctx.respond(
                f"dame un número entero, no \"**{ctx.options.cantidad}**\"",
                user_mentions=False,
                role_mentions=False,
                mentions_everyone=False,
                delete_after=10)
            return

    if amount > coins:
        await ctx.respond("estas apostando más de lo que tienes 🤬",
                          delete_after=10)
        return
    elif amount <= 0:
        await ctx.respond("real? 😳", delete_after=10)
        return

    # actual code

    win = False

    if random.randint(0, 4) <= 1:
        await ctx.bot.db.update_coins(ctx.author.id, coins + amount)
        embed = BetterEmbed(
            title="Has ganado 🤑",
            description=
            f"Apostaste **{amount:,}** <:praycoin:758747635909132387> y ahora tienes **{(coins + amount):,}** <:praycoin:758747635909132387>"
            .replace(",", "."),
            color=0x126F3D)

        win = True
    else:
        await ctx.bot.db.update_coins(ctx.author.id, coins - amount)
        embed = BetterEmbed(
            title="Has perdido 😢",
            description=
            f"Apostaste **{amount:,}** <:praycoin:758747635909132387> y ahora tienes **{(coins - amount):,}** <:praycoin:758747635909132387>"
            .replace(",", "."),
            color=0xFF0000)

    await ctx.respond(embed=embed)

    if win:
        await handle_mission_progression(ctx, 9, amount)


@plugin.command
@lightbulb.add_cooldown(length=5, uses=1, bucket=lightbulb.UserBucket)
@lightbulb.option("cantidad",
                  "La cantidad de dinero que quieres apostar",
                  type=str,
                  required=True)
@lightbulb.command("blackjack",
                   "Apuesta dinero y gana al blackjack para no perderlo")
@lightbulb.implements(lightbulb.SlashCommand)
async def blackjack(ctx: lightbulb.Context):

    # checking and stuff
    coins = await ctx.bot.db.fetch_coins(ctx.author.id)

    if coins == None:
        await ctx.respond("si quieres apostar praycoins, reza primero anda",
                          delete_after=10)
        return

    if ctx.options.cantidad == "all":
        amount = coins
    else:
        try:
            amount = int(ctx.options.cantidad)
        except ValueError:
            await ctx.respond(
                f"dame un número entero, no \"**{ctx.options.cantidad}**\"",
                user_mentions=False,
                role_mentions=False,
                mentions_everyone=False,
                delete_after=10)
            return

    if amount > coins:
        await ctx.respond("estas apostando más de lo que tienes 🤬",
                          delete_after=10)
        return
    elif amount <= 0:
        await ctx.respond("real? 😳", delete_after=10)
        return

    await ctx.bot.db.update_coins_subtract(ctx.author.id, amount)

    # quitar dinero aqui

    # actual code

    # index 0 -> clubs, 1 -> diamonds, 2 -> hearts, 3 -> spades
    # 1 -> ace, 2-10 normal, 11 -> jack, 12 -> queen, 13 -> king
    # if i misspelt something i dont give a shit
    stack = [[i for i in range(1, 14)] for _ in range(4)]

    # getting the cards
    bot_cards = [get_card(stack)]

    # si lo hago en una sola linea [get_card(...), get_card(...)] el primer get_card no poppea la carta
    user_cards = [get_card(stack)]
    user_cards += [get_card(stack)]

    view = views.BlackjackView(timeout=45,
                               stack=stack,
                               user_cards=user_cards,
                               bot_cards=bot_cards,
                               author_id=ctx.author.id)
    # view.add_item(views.SelectAmountButton(disabled=True))

    message = await ctx.respond(BetterEmbed(color=0xFFA749).add_field(
        name=f"Cartas del bot ({count_value([c for _, c in bot_cards])})",
        value="".join([get_card_emoji(*info)
                       for info in bot_cards]) + "<:card:1017157571813052486>",
        inline=True).add_field(
            name=f"Tus cartas ({count_value([c for _, c in user_cards])})",
            value="".join([get_card_emoji(*info) for info in user_cards]),
            inline=True),
                                components=view)

    await view.start(message)
    await view.wait()

    stack = view.stack
    user_cards = view.user_cards

    while count_value([c for _, c in bot_cards]) < 17:
        bot_cards += [get_card(stack)]
    # 32353B

    bot_count = count_value([c for _, c in bot_cards])
    user_count = count_value([c for _, c in user_cards])

    # yucky autoformatter on god
    # !!!!!!!!!!!!!!!! mirar si puedo cambiar count_value de abajo por bot_count y user_count (se podria sin problema pero tengo miedo)
    if bot_count == user_count or (bot_count > 21 and user_count > 21):

        await ctx.bot.db.update_coins_add(ctx.author.id, amount)

        await ctx.edit_last_response(embed=BetterEmbed(
            title="Te quedas igual 🗿", color=0x32353B).add_field(
                name=f"Cartas del bot ({bot_count})",
                value="".join([get_card_emoji(*info) for info in bot_cards]),
                inline=True).add_field(name=f"Tus cartas ({user_count})",
                                       value="".join([
                                           get_card_emoji(*info)
                                           for info in user_cards
                                       ]),
                                       inline=True),
                                     components=[])

    elif (user_count > bot_count and user_count <= 21) or bot_count > 21:
        await ctx.bot.db.update_coins_add(ctx.author.id, amount * 2)

        await ctx.edit_last_response(embed=BetterEmbed(
            title=f"Has ganado {amount} praycoins 🤑".replace(",", "."),
            color=0x126F3D).add_field(
                name=f"Cartas del bot ({bot_count})",
                value="".join([get_card_emoji(*info) for info in bot_cards]),
                inline=True).add_field(name=f"Tus cartas ({user_count})",
                                       value="".join([
                                           get_card_emoji(*info)
                                           for info in user_cards
                                       ]),
                                       inline=True),
                                     components=[])

        await handle_mission_progression(ctx, 9, amount)

    elif (user_count < bot_count and bot_count <= 21) or user_count > 21:
        await ctx.edit_last_response(embed=BetterEmbed(
            title=f"Has perdido {amount} praycoins 😔".replace(",", "."),
            color=0xFF0000).add_field(
                name=f"Cartas del bot ({bot_count})",
                value="".join([get_card_emoji(*info) for info in bot_cards]),
                inline=True).add_field(name=f"Tus cartas ({user_count})",
                                       value="".join([
                                           get_card_emoji(*info)
                                           for info in user_cards
                                       ]),
                                       inline=True),
                                     components=[])


# 5 minutos (en vez de ocho como en el og xd)
# el intent:
# @plugin.command
# @lightbulb.command("test", "s")
# @lightbulb.implements(lightbulb.SlashCommand)
# async def test(ctx: lightbulb.Context):
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
#     await ctx.respond("hola")
# await asyncio.sleep(1)
# await ctx.bot.db.update_user_items(ctx.author.id, 1, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 2, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 3, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 4, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 5, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 6, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 7, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 8, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 9, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 10, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 11, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 12, "add")
# await ctx.bot.db.update_user_items(ctx.author.id, 13, "add")

# async def desafio(ctx: lightbulb.Context):
#     lvl = await fetch_level_only(ctx.bot.mysql, ctx.author.id)

#     if lvl == None:
#         await ctx.respond("si quieres hacer un desafío, reza primero anda",
#                           delete_after=10)
#         return

#     mode = random.randint(0, 2)

#     if mode == 0:
#         a, b = random.randint(1, 100), random.randint(1, 100)

#         op = f"{a} + {b} = ?"
#         sol = a + b
#     elif mode == 1:
#         a, b = random.randint(1, 100), random.randint(1, 100)

#         op = f"{a} - {b} = ?"
#         sol = a - b
#     elif mode == 2:
#         a, b = random.randint(0, 15), random.randint(0, 15)

#         op = f"{a} x {b} = ?"
#         sol = a * b

#     embed = BetterEmbed(
#         title=op,
#         description="Momento operación\nTienes **10** segundos para responder")

#     await ctx.respond(embed=embed)

#     try:
#         m = await ctx.bot.wait_for(
#             hikari.GuildMessageCreateEvent,
#             timeout=10,
#             predicate=lambda m: m.author_id == ctx.author.id)
#     except asyncio.TimeoutError:
#         await ctx.respond("has tardado mucho, no te llevas nada esta vez 😔")
#         return

#     if m.content != str(sol):
#         await ctx.respond(f"que va, la respuesta correcta es **{sol}**")
#         return

#     # reward = random.randint(0, 4)  # 1/4  para conseguir item
#     reward = random.randint(25, 100) * lvl


@tasks.task(m=1, auto_start=True)
async def check_for_hour():
    # runs every minute checking if its xx:00
    # if it is itll start the hourly praycoin task
    # and stop this task

    if datetime.now().minute == 0 and not hourly_praycoin_update.is_running:
        hourly_praycoin_update.start()
        check_for_hour.stop()


@tasks.task(h=1, pass_app=True)
async def hourly_praycoin_update(bot: BruhApp):
    # do i really need to have the query in queries.py
    # and the execute in the db_handler? its just one line idk

    if datetime.now().hour == 0:
        await bot.mysql.execute(
            "UPDATE economy SET coins = coins + abuelas * (iglesias + 1) + (10 * guiris) * (donaciones + 1) + (10000 * angeles);"
        )

        if not daily_check.is_running:
            daily_check.start()

        return

    await bot.mysql.execute(
        "UPDATE economy SET coins = coins + abuelas * (iglesias + 1) + (10 * guiris) * (donaciones + 1);"
    )


@tasks.task(d=1, pass_app=True)
async def daily_check(bot: BruhApp):
    # this is used for the mission creation/deletion
    # and to post stats to the top.gg api
    print(f"EMPEZANDO")

    now = datetime.now()
    d = datetime(now.year, now.month, now.day)

    await bot.mysql.execute("DELETE FROM user_missions WHERE ends_at <= %s",
                            (now, ))

    if now.isoweekday() == 1:
        # chequea si el dia es lunes, porque lunes == 1 por codigo
        await bot.mysql.execute("CALL gen_missions(%s, %s)",
                                (d + timedelta(days=7), True))

    await bot.mysql.execute("CALL gen_missions(%s, %s)",
                            (d + timedelta(days=1), False))

    print(f"termino 👍 {datetime.now() - now}")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
