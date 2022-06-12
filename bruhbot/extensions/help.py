import lightbulb
from lightbulb.utils import nav

import datetime
from core.embed import BetterEmbed

plugin = lightbulb.Plugin("Ayuda")


def build_pages(ctx: lightbulb.Context):

    embeds = []

    for name, plugin in ctx.bot.plugins.items():
        embed = BetterEmbed(
            title=name,
            description=
            f"Para más información sobre estos comandos puedes hacer {ctx.prefix}help [comando] o visitar la [página web](https://mefolloatumadre.tk) del bot",
            color=ctx.get_guild().get_member(
                ctx.app.get_me().id).get_top_role().color,
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc))

        commands = []
        for cmd in set(plugin._all_commands):

            # this is done to prevent double commands (slash command + prefix command)
            # very epic walrus operator 🤤
            if (line := f"{cmd.name} :: {cmd.description}"
                ) not in " ".join(commands):
                commands.append(line)

        commands_str = '\n'.join(commands)

        divisions = []

        for i in range(0, len(commands_str), 1010):
            # estoy completamente lucido, son la 1am y no tengo ni idea de como he hecho/estoy haciendo esto
            # pero me hace sentir bastente 🧠

            o = len(divisions[-1]) if divisions else 0
            j = commands_str[i:1010 + i].count(
                "\n") + o if commands_str[i:1010 +
                                          i].count("\n") + o != 0 else 1
            k = j if j < len(commands) else len(commands)

            divisions.append(commands[o:k])

        divisions_str = ['\n'.join(d) for d in divisions]

        [
            embed.add_field(name=f"Los {'otros ' * i}comandos son:",
                            value=f"""
```asciidoc
{string}
```""") for i, string in enumerate(divisions_str)
        ]
        embeds.append(embed)

    return embeds


def build_command_embed(ctx: lightbulb.Context, cmd: lightbulb.CommandLike):

    aliases = ""
    if cmd.aliases:
        aliases = f" ({', '.join(cmd.aliases)}) "

    options = ""
    if cmd.options:
        options = f" {' '.join(f'<{c}>'.upper() for c in cmd.options)}"

    embed = BetterEmbed(
        title=cmd.name.capitalize(),
        description=f"""```asciidoc
=== Información y uso del comando {cmd.name} ===
{cmd.name}{aliases}{options} :: {cmd.description}

Uso: {ctx.prefix}{cmd.signature}
```""",
        color=ctx.get_guild().get_member(
            ctx.app.get_me().id).get_top_role().color,
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc))

    return embed


@plugin.command
@lightbulb.option("comando",
                  "Muestra la información de ese comando",
                  required=False)
@lightbulb.command(
    "help",
    "Muestra la ayuda del bot",
)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def help_cmd(ctx: lightbulb.Context):
    comando = ctx.options.comando

    if comando:
        if comando := ctx.bot.get_slash_command(comando):
            return await ctx.respond(embed=build_command_embed(ctx, comando))

    # h i really dont know if thats the best way to get the bots color
    embed = BetterEmbed(
        title="Ayuda del bot",
        description=
        f"Para más información sobre los comandos puedes hacer {ctx.prefix}help [comando] o visitar la [página web](http://mefolloatumadre.tk/) del bot",
        color=ctx.get_guild().get_member(
            ctx.app.get_me().id).get_top_role().color,
        timestamp=datetime.datetime.now(tz=datetime.timezone.utc))

    embed.add_field(
        "Comandos de economía", """
```md
Estos son los comandos religiosos y la parte de economia del bot.
Pulsa el 🙏 para ver los comandos
```""")

    embed.add_field(
        "Comandos de imágenes", """
```md
Estos son los comandos con los que puedes hacer/editar fotos.
Pulsa el 🖼️ para ver los comandos
```""")

    embed.add_field(
        "Otros comandos", """
```md
Estos son el resto de comandos, no tienen nada en común y tampoco son tan interesanes.
Pulsa el 😳 para ver los comandos
```""")

    pages = [embed] + build_pages(ctx)

    navigator = nav.ButtonNavigator(pages)
    await navigator.run(ctx)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
