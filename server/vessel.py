import functools
import weakref
import random

from position import Position


def playing_only(f):
    @functools.wraps(f)
    async def wrapper(vessel, data):
        if vessel.frozen:
            return 'Battle not started'
        return await f(vessel, data)
    return wrapper


async def no_send(_):
    pass


class Vessel:
    def __init__(self, universe, hname, stats):
        self.u = weakref.proxy(universe)

        self.frozen = True
        self.hname = hname
        self.hp = stats[0]
        self.attack = stats[1]
        self.speed = stats[2]
        self.detection = stats[3]

        self.set_sender(None)
        self.position = Position(
            self.u,
            [random.randint(0, b) for b in self.u.size]
        )
        self.u.add(self, ['vessel'])

    async def destroy(self):
        await self.send('Vessel destroyed')
        self.set_sender(None)
        self.u.remove(self)

    def set_sender(self, send):
        self.send = send or no_send

    def name(self, secret=False):
        if secret:
            return ':'.join(map(str, self.hname))
        else:
            return ':'.join(map(str, self.hname[:2]))

    async def start(self):
        self.frozen = False
        await self.send({
            'type': 'start_battle',
        })

    async def onMsg_connect(self, data):
        msgs = []
        msgs.append({
            'type': 'stats',
            'hp': self.hp,
            'attack': self.attack,
            'speed': self.speed,
            'detection': self.detection,
        })
        if not self.frozen:
            msgs.append({
                'type': 'start_battle',
            })
        return msgs

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'

    def __str__(self):
        return ''.join([
            f'Vessel(p={self.position}, hp={self.hp}, attack={self.attack}, ',
            f'speed={self.speed}, detection={self.detection}, ',
            f'hname={self.hname})',
        ])
