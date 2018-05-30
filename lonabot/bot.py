import asyncio
import re

from constants import MAX_REMINDERS

from dumbot.dumbaio import Bot


def cmd(text):
    def decorator(f):
        f._trigger = text
        return f
    return decorator


class Lonabot(Bot):
    # Making Dumbot friendlier
    def __init__(self, token):
        super().__init__(token, timeout=10 * 60)
        self._running = False
        self._updates_loop = None
        self._last_id = 0
        self._cmd = []
        self.me = None

    async def start(self):
        self._running = True
        self.me = await self.getMe()
        self._cmd.clear()
        for m in dir(self):
            m = getattr(self, m)
            trigger = getattr(m, '_trigger', None)
            if isinstance(trigger, str):
                self._cmd.append((
                    re.compile(f'{trigger}(@{self.me.username})?').match, m))

        self._updates_loop = asyncio.ensure_future(
            self._updates_loop_impl())

    def stop(self):
        self._running = False
        if self._updates_loop:
            self._updates_loop.cancel()
            self._updates_loop = None

    async def _updates_loop_impl(self):
        while self._running:
            updates = await self.getUpdates(
                offset=self._last_id + 1, timeout=self.timeout)
            if not updates.ok or not updates.data:
                continue

            self._last_id = updates.data[-1].update_id
            for update in updates.data:
                asyncio.ensure_future(self._on_update(update))

    # Actual methods we'll be using
    async def _on_update(self, update):
        if not update.message.text:
            return

        for trigger, method in self._cmd:
            if trigger(update.message.text):
                await method(update)
                return

        await self.sendMessage(chat_id=update.message.from_.id,
                               text='Say what?')

    @cmd(r'/start')
    async def _start(self, update):
        await self.sendMessage(
            chat_id=update.message.chat.id,
            text=f'''
Hi! I'm {self.me.first_name.title()} and running in "reminder" mode.

You can set reminders by using:
`/remindat 17:05 Optional text`
`/remindin    5m Optional text`

Or list those you have by using:
`/status`

Everyone is allowed to use {MAX_REMINDERS} reminders max. No more!

Made with love by @Lonami and hosted by Richard ❤️
'''.strip(), parse_mode='markdown')

    @cmd(r'/(remindat|remindin|status|clear)')
    async def _soon(self, update):
        await self.sendMessage(
            chat_id=update.message.chat.id,
            text='Coming soon!'
        )
