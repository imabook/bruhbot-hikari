from typing import Container
import lightbulb
import hikari

import random
import functools

plugin = lightbulb.Plugin("Libro")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("sql",
                  "sql code to run",
                  modifier=lightbulb.OptionModifier.CONSUME_REST,
                  required=False)
@lightbulb.command("execute", "Ejecuta sql")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
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
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
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
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def _eval(ctx: lightbulb.Context):

    await ctx.respond("...")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("test", "testing command")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def test(ctx: lightbulb.Context):
    # a = "abuelas"
    # b = "economy"
    # QUERY = f"SELECT {a} FROM {b} WHERE id = %s;"
    # data = await ctx.bot.mysql.fetchone(QUERY, (ctx.author.id, ))
    # print(data)
    ...


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
