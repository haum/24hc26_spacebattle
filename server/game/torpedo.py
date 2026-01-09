import weakref

from .vector import Vector


class Torpedo:
    def __init__(self, universe, position, speed, die_time, emitter=None):
        self.u = universe
        self.emitter = weakref.ref(emitter) if emitter else lambda: None
        self.position = Vector(self.u, position)
        self.speed = speed
        self.die = die_time
        self.u.add(self, ['torpedo', 'collidable', 'update'])

    async def onUpdate(self, _dt, t):
        if t >= self.die:
            self.u.remove(self)
            return

        self.position.add(self.speed)
        for o in self.u.iter('collidable'):
            if o != self and o.position.get() == self.position.get():
                self.u.remove(self)
                cls = o.__class__.__name__
                if cls == 'Vessel':
                    await o.damage(20)
                elif cls == 'Mine':
                    self.u.remove(o)

    def __str__(self):
        return ''.join((
            f'Torpedo(p={self.position}, s={self.speed}, ',
            f'l={self.die-self.u.t:.1f})'
        ))
