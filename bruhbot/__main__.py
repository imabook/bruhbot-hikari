# AMONG US
import os

from hikari import Intents
import lightbulb

from dotenv import load_dotenv

load_dotenv()
intents = (Intents.GUILDS | Intents.GUILD_MEMBERS | Intents.GUILD_BANS
           | Intents.GUILD_EMOJIS | Intents.ALL_MESSAGES
           | Intents.GUILD_MESSAGE_REACTIONS | Intents.ALL_MESSAGE_TYPING)

bot = lightbulb.BotApp(token=os.environ["TEST_TOKEN"],
                       intents=intents,
                       prefix="test ")

bot.load_extensions_from("")

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop
        uvloop.install()

    bot.run()