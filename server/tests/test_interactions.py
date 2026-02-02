import pytest

from game.asteroid import Asteroid
from game.mine import Mine
from game.torpedo import Torpedo
from game.universe import Universe
from game.vessel import Vessel

from .utils import run_universe, RadarLogger


@pytest.mark.asyncio
async def test_torpedo_vs_asteoid():
    u = Universe('test', [50, 50])
    Torpedo(u, [10, 10], [-5, 0], 1)
    Asteroid(u, [0, 10])
    radar = RadarLogger(u)

    await run_universe(u, 3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0

    assert len(radar) == 1
    assert radar[0] == { 'type': 'explosion', 'position': [0, 10] }


@pytest.mark.asyncio
async def test_topedo_attacking_vessel_behind_asteroid():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Asteroid(u, [10, 10])
    radar = RadarLogger(u)

    hp = v.hp

    await run_universe(u, 3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp

    assert len(radar) == 1
    assert radar[0] == { 'type': 'explosion', 'position': [10, 10] }


@pytest.mark.asyncio
async def test_topedo_attacking_vessel_behind_asteroid_modulo1():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [40, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Asteroid(u, [10, 10])
    radar = RadarLogger(u)

    hp = v.hp

    await run_universe(u, 3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp

    assert len(radar) == 1
    assert radar[0] == { 'type': 'explosion', 'position': [10, 10] }


@pytest.mark.asyncio
async def test_topedo_attacking_vessel_behind_asteroid_modulo2():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Asteroid(u, [40, 10])
    radar = RadarLogger(u)

    hp = v.hp

    await run_universe(u, 3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp

    assert len(radar) == 1
    assert radar[0] == { 'type': 'explosion', 'position': [40, 10] }


@pytest.mark.asyncio
async def test_topedo_attacking_vessel_behind_another_vessel():
    u = Universe('test', [50, 50])
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [40, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    radar = RadarLogger(u)

    hp1 = v1.hp
    hp2 = v2.hp

    await run_universe(u, 3)

    assert u.len('torpedo') == 0
    assert u.len('vessel') == 2

    assert v1.hp == hp2
    assert v2.hp < hp2

    assert len(radar) == 1
    assert radar[0] == { 'type': 'explosion', 'position': [40, 10] }


@pytest.mark.asyncio
async def test_topedo_attacking_vessel_behind_mine():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Mine(u, [40, 10], 0)
    radar = RadarLogger(u)

    hp = v.hp

    await run_universe(u, 3)

    assert u.len('mine') == 0
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp

    assert len(radar) == 1
    assert radar[0] == { 'type': 'explosion', 'position': [40, 10] }


@pytest.mark.asyncio
async def test_vessels_collision():
    u = Universe('test', [50, 50])
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [31, 10])
    radar = RadarLogger(u)

    hp1 = v1.hp
    hp2 = v2.hp

    await run_universe(u, 1)
    await v1.onMsg_move({'direction': [1,0]})
    await run_universe(u, 3)

    assert v1.hp == hp1 - 15
    assert v2.hp == hp2 - 15

    assert len(radar) == 1
    assert radar[0] == { 'type': 'explosion', 'position': [31, 10]}
