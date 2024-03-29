import datetime
import typing as t
import hikari
import miru

import random
import math

from contextlib import suppress
from database.db_handler import *

from utils.blackjack import *
from core.embed import BetterEmbed

from utils.items import use_item
from utils.misiones import handle_mission_progression

# really gotta rewrite this, wrote it yesterday and im already regretting it
def get_price(i: int, type: str) -> int:
    match type:
        case "abuelas":
            return math.ceil(10 * 5**(i - 1)/4**(i - 1))
        case "iglesias":
            return math.ceil(1000 * 1.3**(i - 1))
        case "amuletos":
            return math.ceil(2**(i + 2) * 10)
        case "guiris":
            return math.ceil(11000 * 1.25**(i - 1))
        case "donaciones":
            return math.ceil(25000 * 1.35**(i - 1))
        case "angeles":
            return math.ceil(35000 * 1.15**(i - 1))


class BuyView(miru.View):

    def __init__(self, author_id: int, *args, **kwargs) -> None:
        self.author_id = author_id # idk if this is the correct way to do it but i couldnt care less it works fine
        self.ignore_ids = []

        self.bought = False
        self.bonus = 0

        super().__init__(*args, **kwargs)

    async def on_timeout(self) -> None:
        await self.message.edit(
            "loco, eres realmente lento\nsi no querías comprar nada, no haberme hablado 👿",
            components=[])
        # seems to give a keyerror only here xd

        with suppress(KeyError):
            self.stop()

    async def view_check(self, ctx: miru.Context) -> bool:
        if ctx.user.id == self.author_id:
            return True

        if ctx.user.id not in self.ignore_ids:
            await ctx.respond(random.choice(["quédate quieto 😡, tú no has hecho el comando", "párate‼️\ntú no has hecho el comando", "si quieres comprar algo tú, haz el comando TÚ", "párate anda, si quieres comprar algo haz el comando tú"]),
                flags=hikari.MessageFlag.EPHEMERAL)

            self.ignore_ids += [ctx.user.id]
        return False


    @miru.button(label=random.choice(
        ["nah, creo que paso", "boff, mejor no ehh", "no sé, mejor me voy"]),
                 style=hikari.ButtonStyle.DANGER,
                 row=2)
    async def stop_button(self, button: miru.Button, ctx: miru.Context):
        await ctx.edit_response("vale pues nada, ya comprarás algo más tarde",
                                components=[])
        self.stop()  # Stop listening for interactions


# OMG OMG OMG instead of passing everything over to the next button i couldve saved everything in the view and get it from there 🗿
class SelectObjectButton(miru.TextSelect):

    def __init__(self, options=[], *args, **kwargs) -> None:
        options = [miru.SelectOption(label=o.capitalize()) for o in options]
        super().__init__(
            options=options,
            placeholder="elije algo que hayas visto en la tienda, no?",
            *args,
            **kwargs)

    async def callback(self, ctx: miru.Context) -> None:
        # so sexy on god 🤤
        match self.values[0].lower():
            case "ángeles":
                object = "angeles"
            case "máquinas de donaciones":
                object = "donaciones"
            case _:
                object = self.values[0].lower()

        QUERY = f"SELECT coins, {object} FROM economy WHERE id = %s;"

        coins, object_count = await ctx.app.mysql.fetchone(QUERY, (ctx.user.id, ))

        amount = 0
        price = 0

        price_map = {} # la verdad es un poco gay usar esto en vez de una list pero bueno

        i = 0
        while len(price_map) < 25 :

            price += get_price(object_count + 1 + i, object)

            if coins < price:
                # if the while results to false means that the cost is too much
                # thus removing the last price increment here
                price -= get_price(object_count + 1 + i, object)

                break
            
            price_map[i + 1] = price

            amount += 1

            i += 1

        ctx.view.children.pop(0)

        if amount == 0:
            await ctx.edit_response(f"no tienes el dinero suficiente como para comprar **{self.values[0].lower()}** rey 😢\ncuesta **{get_price(object_count + 1 + i, object):,}** <:praycoin:758747635909132387> y tienes **{coins}** <:praycoin:758747635909132387>".replace(',', '.'), components=[])
            ctx.view.stop()
            return        
        if amount == 1:
            ctx.view.add_item(YesButton(object=object, count=object_count, amount=amount, price=price_map[amount], item=self.values[0].lower(), row=2))
            
            await ctx.edit_response("vale vale, " + f"estas a punto de comprar **{amount} {self.values[0].lower()}** por **{price_map[amount]:,}** <:praycoin:758747635909132387>\nte quedarán **{(coins - price_map[amount]):,}** <:praycoin:758747635909132387> vale?".replace(",", "."), components=self.view)
            return


        ctx.view.add_item(SelectAmountButton(map=price_map, amount=amount, count=object_count, item=self.values[0].lower(), object=object, coins=coins))

        desc = "\n".join([f"{self.values[0]} x {k} -> {price_map[k]:,} praycoins" for k in price_map]).replace(",", ".")

        await ctx.edit_response(f"**{self.values[0].lower()}** ehh?\nen total puedes comprar **{amount} {self.values[0].lower()}** que serían **{price}** <:praycoin:758747635909132387>\n\naquí te dejo otros precios y tal si no quieres comprar el máximo, tienes **{coins}** <:praycoin:758747635909132387>\n>>> ```ml\n{desc}```",
                                components=ctx.view)


# put both selections, nothing really fancy
# if nothing is selected make the selectamountbutton disabled
# maybe in the future dont remove the selectobjectbutton and cache the prices and all of that shit so people cant abuse it
# ??? ^

class SelectAmountButton(miru.TextSelect):

    def __init__(self, map: int, amount: int, count: int, item: str, coins: int, object: str, *args, **kwargs) -> None:
        self.item = item
        self.map = map
        self.count = count
        self.coins = coins
        self.object = object
        self.amount = amount

        super().__init__(options=[
            miru.SelectOption(label=f"Comprar {i} {item}") for i in range(1, amount + 1)
        ],
                         placeholder="elije una cantidad, no?",
                         *args,
                         **kwargs)

    async def callback(self, ctx: miru.Context) -> None:
        # second "word" is the number
        i = int(self.values[0].split()[1])

        ctx.view.add_item(YesButton(object=self.object, count=self.count, amount=i, price=self.map[i], item=self.item))
        ctx.view.children.pop(0)

        await ctx.edit_response("vale vale, " + f"estas a punto de comprar **{i} {self.item}** por **{self.map[i]:,}** <:praycoin:758747635909132387>\nte quedarán **{(self.coins - self.map[i]):,}** <:praycoin:758747635909132387> vale?".replace(",", "."),
                                components=self.view)

    # def set_amount(self, amount: int) -> None:
    #     self._placeholder = "elije una cantidad, no?"
    #     self.options = [
    #         miru.SelectOption(label=str(i)) for i in range(1, amount + 1)
    #     ]


class YesButton(miru.Button):

    def __init__(self, count: int, amount: int, price: int, item: str, object: str, row: int = 2) -> None:
        self.amount = amount + count

        self.count = count # for the bonus only

        self.object = object
        self.display_item = item
        self.price = price

        super().__init__(style=hikari.ButtonStyle.SUCCESS,
                         label=random.choice([
                             "* comprar *", "toca consumir", "dale, lo compro",
                             "🤑🤑🤑", "venga va va"
                         ]), row=row)

    async def callback(self, ctx: miru.Context) -> None:
        coins = await ctx.app.db.fetch_coins(ctx.user.id)

        if coins - self.price < 0:
            await ctx.edit_response("vaya, parece que ya no tienes el dinero necesario para comprarlo", components=[])
            self.view.stop()
            return

        await ctx.app.db.buy_object(ctx.user.id, coins - self.price, self.object, self.amount)

        await ctx.edit_response(f"perfecto ya tienes **{self.amount} {self.display_item}** 😇 y ahora cuestan **{get_price(self.amount + 1, self.object):,}** <:praycoin:758747635909132387>".replace(",", "."), components=[])

        ctx.view.bought = True
        ctx.view.bonus = self.count

        match self.object:
            case "abuelas":
                ctx.view.bonus = ctx.view.bonus
            case "iglesias":
                ctx.view.bonus *= 2 
            case "amuletos":
                ctx.view.bonus += math.ceil(ctx.view.bonus / 2) 
            case "angeles":
                ctx.view.bonus *= 3 
            case "guiris":
                ctx.view.bonus *= 4
            case "donaciones":
                ctx.view.bonus *= 5

        await handle_mission_progression(ctx, 10, self.count)
        await handle_mission_progression(ctx, 11, self.count)

        self.view.stop()


class BlackjackView(miru.View):

    def __init__(self, stack, user_cards, bot_cards, author_id, *args, **kwargs) -> None:
        self.stack = stack
        self.user_cards = user_cards
        self.bot_cards = bot_cards

        self.author_id = author_id
        self.ignore_ids = []

        # if count_value([c for _, c in self.user_cards]) == 21:
        #     # blackjack
        #     self.stop()

        super().__init__(*args, **kwargs)


    @miru.button(label=random.choice(
        ["me quedo quedo así", "me planto", "yo confío"]),
                 style=hikari.ButtonStyle.DANGER)
    async def stop_button(self, button: miru.Button, ctx: miru.Context):
        self.stop()  # Stop listening for interactions

    @miru.button(label=random.choice(
        ["pásame otra carta", "dame otra", "necesito otra"]), style=hikari.ButtonStyle.SUCCESS)
    async def get_card(self, button: miru.Button, ctx: miru.Context):
        self.user_cards += [get_card(self.stack)]

        if count_value([c for _, c in self.user_cards]) >= 21:
            self.stop()
            return

        await ctx.edit_response(embed=BetterEmbed(color=0xFFA749).add_field(
            name=f"Cartas del bot ({count_value([c for _, c in self.bot_cards])})",
            value="".join([get_card_emoji(*info) for info in self.bot_cards]) +
            "<:card:1017157571813052486>",
            inline=True).add_field(
                name=f"Tus cartas ({count_value([c for _, c in self.user_cards])})",
                value="".join([get_card_emoji(*info) for info in self.user_cards]),
                inline=True), components=self.build())

    async def view_check(self, ctx: miru.Context) -> bool:
        if ctx.user.id == self.author_id:
            return True

        if ctx.user.id not in self.ignore_ids:
            await ctx.respond(random.choice(["quédate quieto 😡, tú no has hecho el comando", "párate‼️\ntú no has hecho el comando", "si quieres apostar dinero tú, haz el comando TÚ", "párate anda, si quieres apostar dinero haz el comando tú", "😦"]),
                flags=hikari.MessageFlag.EPHEMERAL)

            self.ignore_ids += [ctx.user.id]
        return False


class UseItemView(miru.View):

    def __init__(self, author_id, items, *args, **kwargs) -> None:
    
        self.author_id = author_id
        self.ignore_ids = []

        super().__init__(*args, **kwargs)

        self.add_item(SelectItem(items = items, placeholder=random.choice(["pulsa aquí 👿", "elige item", "a ver que tienes"]), options=[miru.SelectOption(label=i[0], emoji=i[2] or "😷") for i in items.values()]))

    async def on_timeout(self) -> None:
        await self.message.edit(random.choice([
            "bueno que te jodan, tardas mucho 👿", "eres muuuuuuy lento 👿"]),
            components=[])
        
    async def view_check(self, ctx: miru.Context) -> bool:
        if ctx.user.id == self.author_id:
            return True

        if ctx.user.id not in self.ignore_ids:
            await ctx.respond(random.choice(["quédate quieto 😡, tú no has hecho el comando", "párate‼️\ntú no has hecho el comando", "si quieres usar un item, haz el comando TÚ", "párate anda, si quieres usar un item haz el comando tú", "😦"]),
                flags=hikari.MessageFlag.EPHEMERAL)

            self.ignore_ids += [ctx.user.id]
        return False

#TODO: TENDRIA QUE CREAR UNA CUSTOM CLASS FLOW `PrivateView` QUE TIENE YA LO DEL VIEW CHECK PARA NO TENER QUE PONERLO EN TODOS

class YesNoView(miru.View):

    def __init__(self, author_id, *args, **kwargs) -> None:
        self.answer = None

        self.author_id = author_id
        self.ignore_ids = []


        super().__init__(*args, **kwargs)

    @miru.button(label=random.choice(["va", "dale", "si", "usalo"]), style=hikari.ButtonStyle.SUCCESS)
    async def yes_button(self, button: miru.Button, ctx: miru.ViewContext):
        self.answer = True
        self.stop()

    @miru.button(label=random.choice(["nah", "no", "mejor no", "que va"]), style=hikari.ButtonStyle.DANGER)
    async def no_button(self, button: miru.Button, ctx: miru.ViewContext):
        self.answer = False
        self.stop()

    async def view_check(self, ctx: miru.Context) -> bool:
        if ctx.user.id == self.author_id:
            return True

        if ctx.user.id not in self.ignore_ids:
            await ctx.respond(random.choice(["quédate quieto 😡, tú no has hecho el comando", "párate‼️\ntú no has hecho el comando", "si quieres usar un item, haz el comando TÚ", "párate anda, si quieres usar un item haz el comando tú", "😦"]),
                flags=hikari.MessageFlag.EPHEMERAL)

            self.ignore_ids += [ctx.user.id]
        return False

    async def on_timeout(self) -> None:
        await self.message.edit(random.choice([
            "bueno que te jodan, tardas mucho 👿‼️", "eres muuuuuuy lento 👿‼️"]),
            components=[])


class SelectItem(miru.TextSelect):

    def __init__(self, items, *args, **kwargs) -> None:
        self.items = items

        super().__init__(*args, **kwargs)

    async def callback(self, ctx: miru.Context) -> None:
        for i in self.items:

            if (self.values[0] == self.items[i][0]):
                
                view = YesNoView(timeout=15, author_id=ctx.author.id)

                message = await ctx.edit_response(f"**{self.items[i][2] or '😷'} {self.items[i][0]}**: {self.items[i][1]}\n\ntienes **{self.items[i][3]}**, quieres usar uno?", components=view)

                await view.start(message)
                await view.wait()

                if view.answer == None:
                    # timed out

                    break
                
                if view.answer:
                    amount = await ctx.bot.db.fetch_item_amount(ctx.author.id, i) # `i` es la id del item 
                    
                    if amount and amount != 0:
                        await ctx.bot.db.update_user_items(ctx.author.id, i, amount - 1)
                        await use_item(ctx, i)

                        break

                    await ctx.edit_response(f"parece que ya no tienes el item\nvuelve a intentarlo no sé", components=None)

                    break
                

                # my guy didnt want to use it
                await ctx.edit_response(f"pues si no querias usarlo para que lo eliges 👿", components=None)
                break

        self.view.stop()

