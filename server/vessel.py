import weakref


class Vessel:
    def __init__(self, game):
        self.g = weakref.proxy(game)
        self.send = lambda _: None

    async def onMsg_ping(self, data):
        await self.send({'type': 'pong', 'n': data.get('n', None)})

    async def onUnknownMsg(self, data):
        return 'Unknown message'
