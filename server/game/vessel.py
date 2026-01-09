import functools

from .vector import Vector
from .torpedo import Torpedo
from .mine import Mine

HP_LUT = [1, 21, 41, 61, 81, 101, 121, 146, 171, 196]


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
    def __init__(self, universe, hname, stats, position):
        self.u = universe

        self.frozen = True
        self.hname = hname
        self.stats = stats

        self.hp = HP_LUT[stats[0]]

        self.send = no_send
        self.position = Vector(self.u, position)
        self.u.add(self, ['vessel', 'collidable', 'update'])

    async def destroy(self):
        await self.send('Vessel destroyed')
        await self.set_sender(None)
        self.u.remove(self)

    async def set_sender(self, send):
        await self.send('Disconnected by another pilot')
        self.send = send or no_send

    def name(self, secret=False):
        if secret:
            return ':'.join(map(str, self.hname))
        else:
            return ':'.join(map(str, self.hname[:2]))

    async def damage(self, n):
        self.hp -= n
        if self.hp <= 0:
            await self.destroy()

    async def start(self):
        self.frozen = False
        await self.send({
            'type': 'start_battle',
        })

    async def onMsg_connect(self, data):
        if data['id'] != self.name(True):
            return 'Connected to another vessel'
        msgs = []
        msgs.append({
            'type': 'stats',
            'stats': self.stats,
            'hp': self.hp,
        })
        if not self.frozen:
            msgs.append({
                'type': 'start_battle',
            })
        return msgs

    @playing_only
    async def onMsg_fire_torpedo(self, data):
        Torpedo(
            self.u, self.position.get(), data['direction'],
            self.u.t+5, self
        )

    @playing_only
    async def onMsg_drop_mine(self, data):
        Mine(
            self.u, self.position.get(),
            self.u.t + max(0.1, data['delay']), self
        )

    @playing_only
    async def onMsg_autodestruction(self, data):
        await self.destroy()

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'

    async def onUpdate(self, _dt, t):
        for o in self.u.iter('collidable'):
            if o != self and o.position.get() == self.position.get():
                cls = o.__class__.__name__
                if cls == 'Mine':
                    if o.enabled_time < t:
                        self.u.remove(o)
                        await self.damage(20)

    def __str__(self):
        stats = ' '.join(map(lambda v, k: f'{k}:{v}', self.stats, 'HASD'))
        return ''.join([
            f'Vessel(p={self.position}, hp={self.hp}, ',
            f'stats=({stats}), ',
            f'hname={self.hname})',
        ])
