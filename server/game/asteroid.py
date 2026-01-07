import weakref

from .vector import Vector


class Asteroid:
    def __init__(self, universe, position):
        self.u = weakref.proxy(universe)
        self.position = Vector(self.u, position)
        self.u.add(self, ['asteroid', 'collidable'])

    async def destroy(self):
        self.u.remove(self)

    def __str__(self):
        return f'Asteroid(p={self.position})'
