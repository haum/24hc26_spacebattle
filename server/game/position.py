class Position:
    def __init__(self, u, pos):
        self.u = u
        if isinstance(pos, int):
            pos = [0]*pos
        self.pos = pos

    def add(self, dp, modulo=True):
        self.pos = list(map(
            lambda x, y, u: (x + y) % u if modulo else x+y,
            self.pos,
            dp + [0] * len(self.u.size),
            self.u.size
        ))

    def get(self, integer=True):
        if integer:
            return list(map(
                lambda x, u: round(x) % u,
                self.pos,
                self.u.size
            ))
        else:
            return self.pos

    def __str__(self):
        p = ', '.join(map(lambda x: f'{x:.1f}', self.pos))
        return f'Position({p})'
