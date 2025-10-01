import weakref


async def no_send(_):
    pass


class Vessel:
    def __init__(self, game):
        self.g = weakref.proxy(game)
        self.reset_send()

    def reset_send(self):
        self.send = no_send

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'
