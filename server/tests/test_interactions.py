import pytest

from game.asteroid import Asteroid
from game.torpedo import Torpedo
from game.universe import Universe
from game.vessel import Vessel


async def run_universe(u, duration):
    for v in u.iter('vessel'):
        await v.start()
    for t in range(duration*10):
        u.t = t/10
        for o in u.iter('update'):
            await o.onUpdate(0.1, u.t)


@pytest.mark.asyncio
async def test_torpedo_vs_asteoid():
    u = Universe('test', [50, 50])
    Torpedo(u, [10, 10], [-5, 0], 1)
    Asteroid(u, [0, 10])

    await run_universe(u, 3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0


@pytest.mark.asyncio
async def test_topedo_attacking_vessel_behind_asteroid():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Asteroid(u, [10, 10])

    hp = v.hp

    await run_universe(u, 3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp


@pytest.mark.asyncio
async def test_topedo_attacking_vessel_behind_asteroid_modulo1():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [40, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Asteroid(u, [10, 10])

    hp = v.hp

    await run_universe(u, 3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp


@pytest.mark.asyncio
async def test_topedo_attacking_vessel_behind_asteroid_modulo2():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Asteroid(u, [40, 10])

    hp = v.hp

    await run_universe(u, 3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp
