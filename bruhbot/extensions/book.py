from email import message
import lightbulb
import hikari

import asyncio
import random
import functools
import ast
import datetime

from core.embed import BetterEmbed

plugin = lightbulb.Plugin("Libro")
plugin.add_checks(lightbulb.guild_only)


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


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        self.insert_returns(body[-1].body)
        self.insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        self.insert_returns(body[-1].body)


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option("code",
                  "code to run",
                  modifier=lightbulb.OptionModifier.CONSUME_REST,
                  required=False)
@lightbulb.command("eval", "Ejecuta código")
@lightbulb.implements(lightbulb.SlashCommand)
async def _eval(ctx: lightbulb.Context):

    # setting the env so i dont have to import everything
    env = {
        'ctx': ctx,
        'bot': ctx.bot,
        'discord': hikari,
        'hikari': hikari,
        'lightbulb': lightbulb,
        '__import__': __import__
    }

    # checking if its a one liner or a discord message link
    # r"https?:\/\/discord\.com\/channels(\/[0-9]{18,}){3}"
    code = ctx.options.code

    if "https://discord.com/channels/" in code:
        try:
            message: hikari.Message = await ctx.bot.rest.fetch_message(
                code.split("/")[-2],
                code.split("/")[-1])

            code = message.content or (await message.attachments[0].read(
            )).decode("UTF-8") if message.attachments else ""
        except hikari.HikariError as error:
            await ctx.respond(
                f"no pude conseguir el código del [mensaje]({code})\npuede que lo hayas copiado mal: `{code}`\n> `{error}`"
            )
            return

    if not code:
        await ctx.respond("realmente no has mandado nada 👍")

    code = code.strip("` ")

    try:
        body = "async def _exec():\n" + "\n".join(f"\t{i}"
                                                  for i in code.splitlines())

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        start = datetime.datetime.now()
        result = (await eval(f"_exec()", env))

        nl = '\n'

        parsed_input = "\n".join([
            "> " + line for line in
            f"```py\n{code if len(code) <= 250 else code[:250] + f'{nl}...'}```"
            .splitlines()
        ])
        parsed_output = "\n".join([
            "> " + line for line in
            f"```py\n{result if len(str(result)) <= 1500 else str(result)[:1500] + f'{nl}...'}```"
            .splitlines()
        ])

        await ctx.respond(
            f"**input:** 👍\n{parsed_input}\n\n**output:** 📠\n{parsed_output}\n\nha tardado **{round((datetime.datetime.now() - start).total_seconds() * 1000, 4)} ms** en ejecutarse ⏰"
        )

    except Exception as e:
        await ctx.respond(f"vaya... ha salido mal\n```prolog\nError {e}```")


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
