import lightbulb
import hikari

plugin = lightbulb.Plugin("Economía")


@plugin.command
@lightbulb.option(
    "member",
    "El miembro que quieras invertir",
    type=hikari.User,
    required=False,
)
@lightbulb.option("no",
                  "asdfasfdasdfasfdasdf",
                  modifier=lightbulb.OptionModifier.CONSUME_REST,
                  required=True,
                  default=41234)
@lightbulb.option("si",
                  "textotextotexto",
                  modifier=lightbulb.OptionModifier.CONSUME_REST,
                  required=False,
                  default="negros")
@lightbulb.command("pray", "Reza para conseguir praycoins", aliases=["p"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def pray(ctx: lightbulb.Context):
    await ctx.respond("among us")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
