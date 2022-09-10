import lightbulb
import hikari

import asyncio

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
    try:
        m = await ctx.bot.wait_for(
            hikari.GuildMessageCreateEvent,
            timeout=10,
            predicate=lambda m: m.author_id == ctx.author.id)
    except asyncio.TimeoutError:
        await ctx.respond("has tardado mucho, no te llevas nada esta vez 😔")
        return

    await ctx.respond(m.content)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
