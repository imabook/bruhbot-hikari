from types import NoneType
import hikari
import lightbulb

empty_kwargs = {
    "content": None,
    "message": None,
    "embed": None,
    "component": None
}


class BetterContext(lightbulb.PrefixContext):

    def get_message(self, _id: int) -> hikari.Message | NoneType:

        if message := self.bot.cache.get_message(_id):
            return message

        return None

    async def respond(self, *args, **kwargs):
        if args and isinstance(args[0], hikari.ResponseType):
            args = args[1:][0]

        if 'attachment' not in kwargs and 'file' not in kwargs and 'delete_after' not in kwargs:
            if self.event.message_id in self.bot.msgcmd:
                try:

                    if args:
                        empty_kwargs["content"] = args[0]

                    kkwargs = empty_kwargs | self.bot.msgcmd[
                        self.event.
                        message_id] | kwargs  # merge two dicts into one

                    # res = await self.edit_last_response(*args, **kwargs)
                    res = await self.bot.rest.edit_message(**kkwargs, )
                except Exception as e:
                    print(e)
                    res = await super().respond(*args, **kwargs)
            else:
                res = await super().respond(*args, **kwargs)

            try:
                msg = await res.message()
            except Exception:
                # then its already the message
                msg = res

            self.bot.msgcmd[self.event.message_id] = {
                "message": msg.id,
                "channel": msg.channel_id
            }

        else:
            res = await super().respond(*args, **kwargs)

        if len(self.bot.msgcmd) > 3:
            del self.bot.msgcmd[next(iter(
                self.bot.msgcmd))]  # to get and delete the first key

            # ill probably have to make that number bigger or only store messages from small/not really active guilds (or whitelisted and make some 🤑💸💸)

        return res
