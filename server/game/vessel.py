import functools
import itertools

from .vector import vector, hypervoxels_line
from .torpedo import Torpedo
from .mine import Mine
from .radar import emit_explosion, emit_move
from .resource import Resource
from messages.game import MAX_STAT
from enum import IntEnum

HP_LUT = [1, 21, 41, 61, 81, 101, 121, 146, 171, 196]
RADAR_LUT = [10, 20, 40, 60, 80, 100, 120, 140, 170, 200]
LASER_LUT = [_//2 for _ in RADAR_LUT]

class STATS(IntEnum):
    H = 0
    A = 1
    S = 2
    R = 3

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


def use_energy(amount):
    def decorator(f):
        @functools.wraps(f)
        async def wrapper(vessel, data):
            energy = amount(vessel) if callable(amount) else amount
            if await vessel.spend_energy(energy):
                return await f(vessel, data)
        return wrapper
    return decorator


async def no_send(_):
    pass


class Vessel:
    def __init__(self, universe, hname, stats, position):
        self.u = universe

        self.frozen = True
        self.hname = hname
        self.stats = stats

        self.hp = HP_LUT[self.stats[STATS.H]]
        self.radar_radius = RADAR_LUT[self.stats[STATS.R]]
        self.energy = ENERGY.max
        self.move = None

        self.send = no_send
        self.position = position
        self.u.add(self, ['vessel', 'collidable', 'update', 'radar'])

    async def destroy(self):
        await self.send('Vessel destroyed')
        await self.set_sender(None)
        self.u.remove(self)
        Resource(self.u, self.position, HP_LUT[self.stats[STATS.H]], destroyed_vessel=True)

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
    @use_energy(lambda self: self.stats[STATS.S]/MAX_STAT*5)
    async def onMsg_move(self, data):
        d = data['direction']
        self.move = d + [0] * (len(self.u.size) - len(d))

    @playing_only
    @use_energy(ENERGY.torpedo)
    async def onMsg_fire_torpedo(self, data):
        Torpedo(
            self.u, self.position,
            vector.autodim(data['direction'], self.u.size, False),
            self.u.t+5, self
        )

    @playing_only
    @use_energy(ENERGY.mine)
    async def onMsg_drop_mine(self, data):
        Mine(
            self.u, self.position,
            self.u.t + max(0.1, data['delay']), self
        )

    @playing_only
    @use_energy(ENERGY.laser)
    async def onMsg_fire_laser(self, data):
        d = vector.mul(data['direction'], 1/vector.norm(data['direction']))
        positions = list(hypervoxels_line(
            self.position,
            vector.add(self.position, vector.mul(d, LASER_LUT[self.stats[STATS.A]])),
            self.u.size
        ))

        touched = sorted(
            (positions.index(o.position), o)
            for o in itertools.chain(
                self.u.iter('collidable', self),
                self.u.iter('farmable', self)
            )
            if o.position in positions
        )

        for i, o in touched:
            cls = o.__class__.__name__
            if cls == 'Mine':
                await emit_explosion(self.u, o)
                self.u.remove(o)
                break
            elif cls == 'Asteroid' or cls == 'Resource':
                break
            elif cls == 'Vessel':
                await o.damage(20)
                break

    @playing_only
    @use_energy(ENERGY.radar)
    async def onMsg_scan_radar(self, data):
        for t in ('asteroid', 'vessel', 'torpedo', 'farmable'):
            for o in self.u.iter(t, self):
                p = vector.mod_relative(
                    vector.sub(o.position, self.position),
                    self.u.size
                )
                if vector.norm(p) < self.radar_radius:
                    await self.send({
                        'type': 'active_scan',
                        'what': t,
                        'position': p,
                    })

    @playing_only
    async def onMsg_autodestruction(self, data):
        await emit_explosion(self.u, self)
        await self.destroy()

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'

    async def onPassiveScan(self, data):
        p = vector.mod_relative(
            vector.sub(data["position"], self.position),
            self.u.size
        )
        if vector.norm(p) < self.radar_radius:
            msg = data | { 'type': 'passive_scan'}
            if data['what'] == 'move':
                del msg['position']
            await self.send(msg)

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

        imove = len(positions)-1

        self.energy = min(self.energy+_dt*ENERGY.regen, ENERGY.max)

        farmables = (
            (positions.index(o.position), o)
            for o in self.u.iter('farmable', self)
            if o.position in positions)

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
                    await emit_explosion(self.u, o)
                    self.u.remove(o)
                    await self.damage(20)
                    imove = i
                    break
            elif cls == 'Asteroid':
                await emit_explosion(self.u, o)
                await self.damage(1_000_000)
                imove = i
                break
            elif cls == 'Vessel' and o != self:
                await emit_explosion(self.u, o)
                await self.damage(15)
                await o.damage(15)
                imove = 0
                break

        if self.move:
            await emit_move(self.u, self.position, self.name(), self.move)
            self.move = None
        self.position = vector.mod(positions[imove], self.u.size)

    def __str__(self):
        stats = ' '.join(map(lambda v, k: f'{k}:{v}', self.stats, 'HASR'))
        return ''.join([
            f'Vessel(p={self.position}, hp={self.hp}, ',
            f'energy=({self.energy}), ',
            f'stats=({stats}), ',
            f'hname={self.hname})',
        ])
