import weakref

from .vector import vector


class Torpedo:
    def __init__(self, universe, position, speed, die_time, emitter=None):
        self.u = universe
        self.emitter = weakref.ref(emitter) if emitter else lambda: None
        self.position = position
        self.speed = speed
        self.die = die_time
        self.u.add(self, ['torpedo', 'collidable', 'update'])

    async def onUpdate(self, _dt, t):
        if t >= self.die:
            self.u.remove(self)
            return

        self.position = vector.add(self.position, self.speed)
        for o in self.u.iter('collidable'):
            if o != self and o.position == self.position:
                self.u.remove(self)
                cls = o.__class__.__name__
                if cls == 'Vessel':
                    await o.damage(20)
                elif cls == 'Mine':
                    self.u.remove(o)

    def __str__(self):
        return ''.join((
            f'Torpedo(p={self.position}, ',
            f's={vector.str(self.speed)}, ',
            f'l={self.die-self.u.t:.1f})'
        ))
