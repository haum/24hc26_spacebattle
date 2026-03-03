class Asteroid:
    def __init__(self, universe, position):
        self.u = universe
        self.position = position
        self.u.add(self, ['asteroid', 'collidable'])

    def __str__(self):
        return f'Asteroid(p={self.position})'
