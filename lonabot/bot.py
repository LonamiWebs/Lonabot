import asyncio

from dumbot.dumbaio import Bot


class Lonabot(Bot):
    # Making Dumbot friendlier
    def __init__(self, token):
        super().__init__(token, timeout=10 * 60)
        self._running = False
        self._updates_loop = None
        self._last_id = 0

    def start(self):
        self._running = True
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
        print(await self.sendMessage(chat_id=update.message.from_.id,
                                     text=update.message.text[::-1]))
