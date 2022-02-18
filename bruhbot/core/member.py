import hikari
import lightbulb


class BetterMemberConverter(lightbulb.MemberConverter):

    async def convert(self, arg: str) -> hikari.Member:
        try:
            return super().convert(arg)
        except Exception:
            pass

        #nah dont have the time to do this today xd
