import functools
import typing as t

import hikari

import lightbulb

from lightbulb import commands
from lightbulb import cooldowns
from lightbulb import context

lightbulb.cooldowns


class CustomCooldowns:


    # piece of code taken from lightbulb.decorators blessed 🙏
    @staticmethod
    def add_custom_cooldown(
        uses: t.Optional[int] = None,
        bucket: t.Optional[t.Type[cooldowns.Bucket]] = None,
        *,
        callback: t.Optional[t.Callable[[context.base.Context], t.Union[
            cooldowns.Bucket, t.Coroutine[t.Any, t.Any,
                                          cooldowns.Bucket]]]] = None,
        cls: t.Type[cooldowns.CooldownManager] = cooldowns.CooldownManager,
        **kwargs
    ) -> t.Callable[[commands.base.CommandLike], commands.base.CommandLike]:
        """
        Second order decorator that sets the cooldown manager for a command.

        Args:
            uses (:obj:`int`): The number of command invocations before the cooldown will be triggered.
            bucket (Type[:obj:`~.cooldowns.Bucket`]): The bucket to use for cooldowns.

        Keyword Args:
            callback (Callable[[:obj:`~.context.base.Context], Union[:obj:`~.cooldowns.Bucket`, Coroutine[Any, Any, :obj:`~.cooldowns.Bucket`]]]): Callable
                that takes the context the command was invoked under and returns the appropriate bucket object to use for
                cooldowns in the context.
            cls (Type[:obj:`~.cooldowns.CooldownManager`]): The cooldown manager class to use. Defaults to
                :obj:`~.cooldowns.CooldownManager`.
        """
        getter: t.Callable[[context.base.Context],
                           t.Union[cooldowns.Bucket,
                                   t.Coroutine[t.Any, t.Any,
                                               cooldowns.Bucket]]]

        if uses is not None and bucket is not None:

            def _get_bucket(_: context.base.Context,
                            b: t.Type[cooldowns.Bucket], l: float,
                            u: int) -> cooldowns.Bucket:
                return b(l, u)

            getter = functools.partial(_get_bucket, b=bucket, l=10, u=uses)
        elif callback is not None:
            getter = callback
        else:
            raise TypeError(
                "Invalid arguments - either provided all of the args length,uses,bucket or the kwarg callback"
            )

        def decorate(
                c_like: commands.base.CommandLike
        ) -> commands.base.CommandLike:
            if not isinstance(c_like, commands.base.CommandLike):
                raise SyntaxError(
                    "'add_cooldown' decorator must be above the 'command' decorator"
                )

            c_like.cooldown_manager = cls(getter)
            return c_like

        return decorate
