from types import SimpleNamespace

def hypervoxels_line(p0, p1, u=None):
    p0 = list(p0)
    p1 = list(p1)
    dim = len(p0)

    delta = [abs(p1[i] - p0[i]) for i in range(dim)]
    step = [1 if p1[i] > p0[i] else -1 for i in range(dim)]
    axis = max(range(dim), key=lambda i: delta[i])

    errors = [delta[axis] // 2 for _ in range(dim)]
    p = p0[:]

    for _ in range(int(delta[axis])+1):
        yield list(map(
            lambda x, u: round(x) % u,
            p,
            u
        )) if u else vector_round(p)

        for i in range(dim):
            if i == axis:
                continue
            errors[i] -= delta[i]
            if errors[i] < 0:
                p[i] += step[i]
                errors[i] += delta[axis]
        p[axis] += step[axis]

def vector_autodim(v, u, modulo=True):
    p = (v + [0] * (len(u) - len(v)))[:len(u)]
    if modulo:
        p = vector_mod(p, u)
    return p

def vector_mod(v, u):
    return list(map(lambda a, b: a%b, v, u))

def vector_mod_relative(v, u):
    return list(map(lambda a, b: m if (m:= a%b) < b/2 else m - b, v, u))

def vector_add(v1, v2):
    if isinstance(v2, list):
        return list(map(lambda a, b: a+b, v1, v2))
    return [i+v2 for i in v1]

def vector_sub(v1, v2):
    if isinstance(v2, list):
        return list(map(lambda a, b: a-b, v1, v2))
    return [i-v2 for i in v1]

def vector_mul(v, k):
    return [i*k for i in v]

def vector_round(v):
    return [round(i) for i in v]

def vector_str(v):
    p = ', '.join(map(lambda x: f'{x:.1f}', v))
    return f'[{p}]'

vector = SimpleNamespace(
    autodim=vector_autodim,
    mod=vector_mod,
    mod_relative=vector_mod_relative,
    add=vector_add,
    sub=vector_sub,
    mul=vector_mul,
    str=vector_str,
)
