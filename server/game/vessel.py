import functools
import itertools
import random

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
IEM_LUT = [int(_*1.2) for _ in RADAR_LUT]
MOVE_LUT = [int(_*1.5) for _ in RADAR_LUT]

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
    radar = 5
    broadcast = 40
    regen = 4
    max = 100

def playing_only(f):
    @functools.wraps(f)
    async def wrapper(vessel, data):
        if vessel.frozen:
            await vessel.damage(1)
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


def iem_sensitive(f):
    @functools.wraps(f)
    async def wrapper(vessel, data):
        if vessel.iemed_until > vessel.u.t:
            await vessel.damage(1)
            await vessel.send({'type': 'iem_frozen'})
        else:
            return await f(vessel, data)
    return wrapper


async def no_send(_):
    pass


class Vessel:
    def __init__(self, universe, hname, stats, position):
        self.u = universe

        self.frozen = True
        self.iemed_until = 0
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
        self.hp = max(self.hp - n, 0)
        await self.send({ 'type': 'damage', 'hp': self.hp })
        if self.hp <= 0:
            await self.destroy()

    async def spend_energy(self, n):
        if self.energy < n:
            await self.damage(1)
            await self.send({'type': 'low_energy'})
            return False
        self.energy = max(0, self.energy-n)
        return True

    async def start(self):
        self.frozen = False
        await self.send({
            'type': 'start_battle',
        })

    async def register_iem(self, t_end):
        await self.send({'type': 'iem_damage'})
        self.iemed_until = t_end

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
    @iem_sensitive
    async def onMsg_move(self, data):
        d = vector.autodim(data['direction'], self.u.size, False)
        dlen = vector.norm(d)
        dmax = MOVE_LUT[self.stats[STATS.S]]
        energy = min(dlen/dmax * ENERGY.move, ENERGY.move)
        if await self.spend_energy(energy):
            if dlen <= dmax:
                self.move = d
            else:
                await self.damage(1)
                return {'type': 'move_aborded'}

    @playing_only
    @iem_sensitive
    @use_energy(ENERGY.torpedo)
    async def onMsg_fire_torpedo(self, data):
        Torpedo(
            self.u, self.position,
            vector.autodim(data['direction'], self.u.size, False),
            self.u.t+5, self
        )

    @playing_only
    @iem_sensitive
    @use_energy(ENERGY.mine)
    async def onMsg_drop_mine(self, data):
        Mine(
            self.u, self.position,
            self.u.t + max(0.1, data['delay']), self
        )

    @playing_only
    @iem_sensitive
    @use_energy(ENERGY.laser)
    async def onMsg_fire_laser(self, data):
        d = vector.mul(data['direction'], 1/vector.norm(data['direction']))
        positions = list(hypervoxels_line(
            self.position,
            vector.add(self.position, vector.mul(d, LASER_LUT[self.stats[STATS.A]])),
            self.u.size
        ))

        touched = sorted((
            (positions.index(o.position), o)
            for o in itertools.chain(
                self.u.iter('collidable', self),
                self.u.iter('resource', self)
            )
            if o.position in positions
        ), key=lambda x:x[0])

        for i, o in touched:
            cls = o.__class__.__name__
            if cls == 'Mine':
                await o.destroy()
                break
            elif cls == 'Asteroid' or cls == 'Resource':
                break
            elif cls == 'Vessel':
                await o.damage(20)
                break

    @playing_only
    @iem_sensitive
    @use_energy(ENERGY.iem)
    async def onMsg_fire_iem(self, data):
        d = vector.mul(data['direction'], 1/vector.norm(data['direction']))
        positions = list(hypervoxels_line(
            self.position,
            vector.add(self.position, vector.mul(d, IEM_LUT[self.stats[STATS.A]])),
            self.u.size
        ))

        touched = sorted((
            (positions.index(o.position), o)
            for o in self.u.iter('collidable', self)
            if o.position in positions
        ), key=lambda x:x[0])

        for i, o in touched:
            cls = o.__class__.__name__
            if cls == 'Vessel':
                await o.register_iem(self.u.t + 5)

    @playing_only
    @iem_sensitive
    @use_energy(ENERGY.radar)
    async def onMsg_scan_radar(self, data):
        for t in ('asteroid', 'mine', 'vessel', 'torpedo', 'resource'):
            for o in self.u.iter(t, self):
                p = vector.mod_relative(
                    vector.sub(o.position, self.position),
                    self.u.size
                )
                if vector.manhattan(p) < self.radar_radius:
                    await self.send({
                        'type': 'active_scan',
                        'what': t,
                        'position': p,
                    })

    @playing_only
    @iem_sensitive
    async def onMsg_broadcast(self, data):
        anonymous = data.get('anonymous', False)
        cost = ENERGY.broadcast * (2 if anonymous else 1)
        if not await self.spend_energy(cost):
            return
        for v in self.u.iter('vessel', self):
            rel = vector.mod_relative(
                vector.sub(v.position, self.position),
                self.u.size
            )
            dist = vector.norm(rel)
            p = max(0.0, 1 - dist / (max(self.u.size)/4))
            if random.random() < p:
                msg = {
                    'type': 'broadcast',
                    'message': data['message'],
                    'position': rel,
                }
                if not anonymous:
                    msg['emitter'] = self.name()
                await v.send(msg)

    @playing_only
    async def onMsg_autodestruction(self, data):
        await emit_explosion(self.u, self)
        await self.destroy()
        objects_within_range = (o
            for o in self.u.iter('collidable', self)
            if vector.norm(vector.mod_relative(
                vector.sub(o.position, self.position),
                self.u.size
            )) < 5
        )
        for o in objects_within_range:
            cls = o.__class__.__name__
            if cls == 'Vessel':
                await o.damage(20)
            if cls == 'Mine':
                await o.destroy()

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'

    @iem_sensitive
    async def onPassiveScan(self, data):
        p = vector.mod_relative(
            vector.sub(data["position"], self.position),
            self.u.size
        )
        if vector.manhattan(p) < self.radar_radius:
            msg = data | { 'type': 'passive_scan'}
            msg['position'] = p
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
        explosions = []
        mines = []
        damages = []

        self.energy = min(self.energy+_dt*ENERGY.regen, ENERGY.max)

        resources = (
            (positions.index(o.position), o)
            for o in self.u.iter('resource', self)
            if o.position in positions)

        for i, o in resources:
            qantity, cont = await o.harvest(_dt)
            old_energy = self.energy
            self.energy = min(self.energy + qantity, ENERGY.max)
            if old_energy < ENERGY.max and self.energy == ENERGY.max:
                await self.send({'type': 'resource_fullcharge'})
            if not cont:
                await self.send({'type': 'resource_depleted'})

        booms = sorted((
            (positions.index(o.position), o)
            for o in self.u.iter('collidable', self)
            if o.position in positions
        ), key=lambda x:x[0])

        for i, o in booms:
            cls = o.__class__.__name__
            if cls == 'Mine':
                if o.enabled_time < t:
                    mines.append(o)
                    imove = i
                    break
            elif cls == 'Asteroid':
                explosions.append(o)
                damages.append((self, 1_000_000))
                imove = i
                break
            elif cls == 'Vessel' and o != self:
                explosions.append(o)
                explosions.append(self)
                damages += [(self, 15), (o, 15)]
                imove = i-1
                break

        if self.move:
            await emit_move(
                self.u, self.position, self.name(),
                vector.mod_relative(vector.sub(positions[imove], self.position), self.u.size)
            )
            self.move = None
        self.position = vector.mod(positions[imove], self.u.size)
        for o in explosions:
            await emit_explosion(self.u, o)
        for o in mines:
            await o.destroy()
        for o, amount in damages:
            await o.damage(amount)

    def __str__(self):
        stats = ' '.join(map(lambda v, k: f'{k}:{v}', self.stats, 'HASR'))
        return ''.join([
            f'Vessel(p={self.position}, hp={self.hp}, ',
            f'energy=({self.energy}), ',
            f'stats=({stats}), ',
            f'hname=({self.name()})',
        ])
