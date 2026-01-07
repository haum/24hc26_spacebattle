import weakref
import time

from .vector import Vector


class Torpedo:
    def __init__(self, universe, position, speed, lifetime, emitter=None):
        self.u = universe
        self.emitter = weakref.ref(emitter) if emitter else lambda: None
        self.position = Vector(self.u, position)
        self.speed = speed
        self.die = time.time() + lifetime
        self.u.add(self, ['torpedo', 'collidable', 'update'])

    async def onUpdate(self, _dt, _t):
        if time.time() >= self.die:
            self.u.remove(self)
            return

        self.position.add(self.speed)
        for o in self.u.iter('collidable'):
            if o != self and o.position.get() == self.position.get():
                self.u.remove(self)
                cls = o.__class__.__name__
                if cls == 'Vessel':
                    await o.damage(20)

    def __str__(self):
        return ''.join((
            f'Torpedo(p={self.position}, s={self.speed}, ',
            f'l={self.die-time.time():.1f})'
        ))
