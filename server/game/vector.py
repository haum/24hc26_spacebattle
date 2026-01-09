def hypervoxels_line(p0, p1, u=None):
    p0 = list(p0)
    p1 = list(p1)
    dim = len(p0)

    delta = [abs(p1[i] - p0[i]) for i in range(dim)]
    step = [1 if p1[i] > p0[i] else -1 for i in range(dim)]
    axis = max(range(dim), key=lambda i: delta[i])

    errors = [delta[axis] // 2 for _ in range(dim)]
    p = p0[:]

    while True:
        yield list(map(
            lambda x, u: round(x) % u,
            p,
            u
        )) if u else p[:]

        if p == p1:
            break

        for i in range(dim):
            if i == axis:
                continue
            errors[i] -= delta[i]
            if errors[i] < 0:
                p[i] += step[i]
                errors[i] += delta[axis]
        p[axis] += step[axis]


class Vector:
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
        return f'Vector({p})'
