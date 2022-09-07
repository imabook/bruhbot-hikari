from typing import Container
import lightbulb
import hikari

import random
import functools

from core.embed import BetterEmbed

plugin = lightbulb.Plugin("Libro")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("sql",
                  "sql code to run",
                  modifier=lightbulb.OptionModifier.CONSUME_REST,
                  required=False)
@lightbulb.command("execute", "Ejecuta sql")
@lightbulb.implements(lightbulb.SlashCommand)
async def execute(ctx: lightbulb.Context):
    response = await ctx.bot.mysql.execute(ctx.options.sql)
    await ctx.respond(response)


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("sql",
                  "sql code to run",
                  modifier=lightbulb.OptionModifier.CONSUME_REST,
                  required=False)
@lightbulb.command("fetch", "Ejecuta sql")
@lightbulb.implements(lightbulb.SlashCommand)
async def fetch(ctx: lightbulb.Context):
    response = await ctx.bot.mysql.fetch(ctx.options.sql)
    await ctx.respond("\n".join([str(r) for r in response]))


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("code",
                  "code to run",
                  modifier=lightbulb.OptionModifier.CONSUME_REST,
                  required=False)
@lightbulb.command("eval", "Ejecuta código")
@lightbulb.implements(lightbulb.SlashCommand)
async def _eval(ctx: lightbulb.Context):

    await ctx.respond("...")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("test", "testing command")
@lightbulb.implements(lightbulb.SlashCommand)
async def test(ctx: lightbulb.Context):
    await ctx.respond(embed=BetterEmbed().add_field(
        name="bots cards", value="<:2c:1017108232738709556>"))


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
