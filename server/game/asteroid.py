from .vector import vector


class Asteroid:
    def __init__(self, universe, position):
        self.u = universe
        self.position = vector.autodim(position, self.u.size)
        self.u.add(self, ['asteroid', 'collidable'])

    async def destroy(self):
        self.u.remove(self)

    def __str__(self):
        return f'Asteroid(p={vector.str(self.position)})'
