import hikari
import random

FOOTERS = [
    "eduardo 👍", "fumar oficial 🚬", "#drillespañol 😈", "yo literal 🚶",
    "orslon llevame al interneto porfav 😨", "no puedo mas",
    "fuente: lo vi en tiktok 🌝", "2013 va a ser mi año 📦", "que haces 💀",
    "npc? 📸", "checkea chepa 🐒", "no publico mis logros porque no tengo 🧐",
    "texto ejemplo", "willy no quiero tu golem en serio 😪", "i love lean 💜",
    "me gusta este pez 🐟", "cachimbacraft? 😇", "lo hize yo", "HELP ME 冰冷是個笑話",
    f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
    "yo y los tirando facts cuando:", "eres real?", "psicótico 😁", "humilde",
    "BING CHILLING 🍦", "enterprise community edition 💸", "con flow tarantula",
    "cada día peor y no lo entiendo", "j", "te echo de menos sewerslvt 😢",
    "momento gitano? 😨"
]


class BetterEmbed(hikari.Embed):

    def __init__(self, *, color=None, **kwargs) -> None:

        if not color:
            color = hikari.Color(0x2f3136)

        super().__init__(color=color, **kwargs)

        self.set_footer(random.choice(FOOTERS))
