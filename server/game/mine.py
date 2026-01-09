import weakref

from .vector import Vector


class Mine:
    def __init__(self, universe, position, enabled_time, emitter=None):
        self.u = universe
        self.emitter = weakref.ref(emitter) if emitter else lambda: None
        self.position = Vector(self.u, position)
        self.enabled_time = enabled_time
        self.u.add(self, ['mine', 'collidable'])

    def __str__(self):
        return f'Mine(p={self.position})'
