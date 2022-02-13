import hikari
import random


class BetterEmbed(hikari.Embed):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        if "color" not in kwargs.keys():
            self.color = hikari.Color(0x2f3136)

        self.set_footer(
            random.choice([
                "eduardo 👍", "fumar oficial 🚬", "#drillespañol 😈",
                "yo literal 🚶", "orslon llevame al interneto porfav 😨",
                "no puedo mas", "fuente: lo vi en tiktok 🌝",
                "2013 va a ser mi año 📦", "que haces 💀", "npc? 📸",
                "checkea chepa 🐒", "no publico mis logros porque no tengo 🧐",
                "texto ejemplo", "willy no quiero tu golem en serio 😪"
            ]))
