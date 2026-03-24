import weakref

from .vector import vector, hypervoxels_line
from .radar import emit_explosion
from .observer import emit_observer_msg


class Torpedo:
    def __init__(self, universe, position, speed, die_time, emitter=None):
        self.u = universe
        self.emitter = weakref.ref(emitter) if emitter else lambda: None
        self.position = position
        self.speed = speed
        self.die = die_time
        self.activated = False
        self.u.add(self, ['torpedo', 'collidable', 'update'])

    async def onUpdate(self, _dt, t):
        if t >= self.die:
            self.u.remove(self)
            return

        if not self.activated:
            if self.emitter():
                if self.position != self.emitter().position:
                    self.activated = True
            else:
                self.activated = True

        positions = list(hypervoxels_line(
            self.position,
            vector.add(self.position, self.speed),
            self.u.size
        ))

        booms = sorted((
            (positions.index(o.position), o)
            for o in self.u.iter('collidable', self)
            if o.position in positions
        ), key=lambda x:x[0])

        for i, o in booms:
            cls = o.__class__.__name__
            if cls == 'Vessel':
                if o != self.emitter() or self.activated:
                    self.u.remove(self)
                    await emit_explosion(self.u, o)
                    await emit_observer_msg(self.u, f'{o.name()} hit by torpedo!')
                    await o.damage(20)
                    break
            elif cls == 'Asteroid':
                await emit_explosion(self.u, o)
                self.u.remove(self)
                break
            elif cls == 'Mine':
                mine_owner = o.emitter or 'someone'
                await emit_observer_msg(self.u, f"One of {mine_owner}'s mine got hit by torpedo!")
                await o.destroy()
                self.u.remove(self)
                break

        self.position = positions[-1]

    def __str__(self):
        return ''.join((
            f'Torpedo(p={self.position}, ',
            f's={vector.str(self.speed)}, ',
            f'l={self.die-self.u.t:.1f})'
        ))
