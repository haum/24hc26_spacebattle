import weakref


async def no_send(_):
    pass


class Vessel:
    def __init__(self, game, universe, stats):
        self.g = weakref.proxy(game)
        self.u = weakref.proxy(universe)

        self.hp = stats[0]
        self.attack = stats[1]
        self.speed = stats[2]
        self.detection = stats[3]

        self.reset_send()

    async def destroy(self):
        await self.send('Vessel destroyed')
        self.reset_send()
        self.u.remove_vessel(self)

    def reset_send(self):
        self.send = no_send

    def name(self):
        return next(k for k, v in self.g.vessels.items() if v == self)

    async def onMsg_connect(self, data):
        return {
            'type': 'stats',
            'hp': self.hp,
            'attack': self.attack,
            'speed': self.speed,
            'detection': self.detection,
        }

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'
