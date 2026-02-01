import functools

from .vector import vector, hypervoxels_line
from .torpedo import Torpedo
from .mine import Mine
from .resource import Resource
from messages.game import MAX_STAT
from enum import IntEnum

HP_LUT = [1, 21, 41, 61, 81, 101, 121, 146, 171, 196]

class STATS(IntEnum):
    H = 0
    A = 1
    S = 2
    D = 3

class ENERGY:
    torpedo = 10
    mine = 10
    iem = 30
    laser = 50
    move = 5
    radar = 1
    regen = 10
    max = 100

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

        self.hp = HP_LUT[self.stats[STATS.H]]
        self.energy = ENERGY.max
        self.move = None

        self.send = no_send
        self.position = position
        self.u.add(self, ['vessel', 'collidable', 'update'])

    async def destroy(self):
        await self.send('Vessel destroyed')
        await self.set_sender(None)
        self.u.remove(self)
        Resource(self.u, self.position, HP_LUT[self.stats[STATS.H]])

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

    async def spend_energy(self, n):
        if self.energy < n:
            await self.send({'type': 'low_energy'})
            return False
        self.energy = max(0, self.energy-n)
        return True

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
    async def onMsg_move(self, data):
        if await self.spend_energy(self.stats[STATS.S]/MAX_STAT*5):
            d = data['direction']
            self.move = d + [0] * (len(self.u.size) - len(d))

    @playing_only
    async def onMsg_fire_torpedo(self, data):
        if await self.spend_energy(ENERGY.torpedo):
            Torpedo(
                self.u, self.position,
                vector.autodim(data['direction'], self.u.size, False),
                self.u.t+5, self
            )

    @playing_only
    async def onMsg_drop_mine(self, data):
        if await self.spend_energy(ENERGY.mine):
            Mine(
                self.u, self.position,
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
        positions = [self.position]
        if self.move:
            positions = list(hypervoxels_line(
                self.position,
                list(map(
                    lambda p, v: p+v,
                    self.position,
                    self.move
                )),
                self.u.size
            ))
            self.move = None

        imove = len(positions)-1

        self.energy = min(self.energy+_dt*ENERGY.regen, ENERGY.max)

        farmables = sorted(
            (positions.index(o.position), o)
            for o in self.u.iter('farmable', self)
            if o.position in positions
        )

        for i, o in farmables:
            qantity, cont = await o.harvest(_dt)
            self.energy = min(self.energy + qantity, ENERGY.max)
            if not cont:
                await self.send({'type': 'resource_depleted'})

        booms = sorted(
            (positions.index(o.position), o)
            for o in self.u.iter('collidable', self)
            if o.position in positions
        )

        for i, o in booms:
            cls = o.__class__.__name__
            if cls == 'Mine':
                if o.enabled_time < t:
                    self.u.remove(o)
                    await self.damage(20)
                    imove = i
                    break
            elif cls == 'Asteroid':
                await self.damage(1_000_000)
                imove = i
                break

        self.position = vector.mod(positions[imove], self.u.size)

    def __str__(self):
        stats = ' '.join(map(lambda v, k: f'{k}:{v}', self.stats, 'HASD'))
        return ''.join([
            f'Vessel(p={self.position}, hp={self.hp}, ',
            f'stats=({stats}), ',
            f'hname={self.hname})',
        ])
