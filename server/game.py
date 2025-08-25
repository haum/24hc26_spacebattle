import weakref


class Vessel:
    def __init__(self, game):
        self.g = weakref.proxy(game)
        self.send = lambda _: None

    async def onMsg_coucou(self, data):
        await self.send({'type': 'coucouback'})

    async def onUnknownMsg(self, data):
        return "Unknown"


class Game:
    def __init__(self):
        self.vessels = {
            'sIjdR': Vessel(self),
            'hsUje': Vessel(self),
            'Wjdol': Vessel(self),
            'ppdOd': Vessel(self),
            'NnsgT': Vessel(self),
        }
