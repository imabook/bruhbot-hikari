import lightbulb

plugin = lightbulb.Plugin("Economía")


@plugin.command
@lightbulb.command("pray", "Reza para conseguir praycoins", aliases=["p"])
@lightbulb.implements(lightbulb.PrefixCommand)
async def pray(ctx: lightbulb.Context):
    await ctx.respond("among us")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
