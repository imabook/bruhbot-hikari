import hikari
import random


class BetterEmbed(hikari.Embed):

    def __init__(self, *, color=None, **kwargs) -> None:

        if not color:
            color = hikari.Color(0x2f3136)

        super().__init__(color=color, **kwargs)

        self.set_footer(
            random.choice([
                "eduardo π", "fumar oficial π¬", "#drillespaΓ±ol π",
                "yo literal πΆ", "orslon llevame al interneto porfav π¨",
                "no puedo mas", "fuente: lo vi en tiktok π",
                "2013 va a ser mi aΓ±o π¦", "que haces π", "npc? πΈ",
                "checkea chepa π", "no publico mis logros porque no tengo π§",
                "texto ejemplo", "willy no quiero tu golem en serio πͺ",
                "i love lean π"
            ]))
