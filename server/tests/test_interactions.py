import pytest

from game.asteroid import Asteroid
from game.mine import Mine
from game.torpedo import Torpedo
from game.universe import Universe
from game.vessel import Vessel

from .utils import UniverseRunner, RadarLogger, MessageLogger


@pytest.mark.asyncio
async def test_torpedo_vs_asteroid():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    Torpedo(u, [10, 10], [-5, 0], 1)
    Asteroid(u, [0, 10])
    radar = RadarLogger(u)

    await runner.run_for(3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0

    assert len(radar) == 1
    assert radar[0] == { 'what': 'explosion', 'position': [0, 10] }


@pytest.mark.asyncio
async def test_torpedo_attacking_vessel_behind_asteroid():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Asteroid(u, [10, 10])
    radar = RadarLogger(u)

    hp = v.hp

    await runner.run_for(3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp

    assert len(radar) == 1
    assert radar[0] == { 'what': 'explosion', 'position': [10, 10] }


@pytest.mark.asyncio
async def test_torpedo_attacking_vessel_behind_asteroid_modulo1():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [40, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Asteroid(u, [10, 10])
    radar = RadarLogger(u)

    hp = v.hp

    await runner.run_for(3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp

    assert len(radar) == 1
    assert radar[0] == { 'what': 'explosion', 'position': [10, 10] }


@pytest.mark.asyncio
async def test_torpedo_attacking_vessel_behind_asteroid_modulo2():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Asteroid(u, [40, 10])
    radar = RadarLogger(u)

    hp = v.hp

    await runner.run_for(3)

    assert u.len('asteroid') == 1
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp

    assert len(radar) == 1
    assert radar[0] == { 'what': 'explosion', 'position': [40, 10] }


@pytest.mark.asyncio
async def test_torpedo_attacking_vessel_behind_another_vessel():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [40, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    radar = RadarLogger(u)

    hp1 = v1.hp
    hp2 = v2.hp

    await runner.run_for(3)

    assert u.len('torpedo') == 0
    assert u.len('vessel') == 2

    assert v1.hp == hp2
    assert v2.hp < hp2

    assert len(radar) == 1
    assert radar[0] == { 'what': 'explosion', 'position': [40, 10] }


@pytest.mark.asyncio
async def test_torpedo_attacking_vessel_behind_mine():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    Torpedo(u, [20, 10], [-5, 0], 1)
    Mine(u, [40, 10], 0)
    radar = RadarLogger(u)

    hp = v.hp

    await runner.run_for(3)

    assert u.len('mine') == 0
    assert u.len('torpedo') == 0
    assert u.len('vessel') == 1

    assert v.hp == hp

    assert len(radar) == 1
    assert radar[0] == { 'what': 'explosion', 'position': [40, 10] }


@pytest.mark.asyncio
async def test_vessels_collision():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [31, 10])
    radar = RadarLogger(u)

    hp1 = v1.hp
    hp2 = v2.hp

    await runner.run_for(1)
    await v1.onMsg_move({'direction': [1,0]})
    await runner.run_for(3)

    assert v1.hp == hp1 - 15
    assert v2.hp == hp2 - 15

    assert len(radar) == 2
    assert radar[0] == { 'what': 'explosion', 'position': [31, 10]}


@pytest.mark.asyncio
async def test_vessel_collision_with_mine():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    Mine(u, [29, 10], u.t)

    hp = v1.hp

    await runner.run_for(1)
    await v1.onMsg_move({'direction': [-1, 0]})
    await runner.run_for(3)

    assert u.len('mine') == 0
    assert v1.hp == hp - 20


@pytest.mark.asyncio
async def test_mine_chainreaction():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    m1 = Mine(u, [30, 10], u.t)
    m2 = Mine(u, [34, 10], u.t)
    radar = RadarLogger(u)

    await runner.run_for(1)
    await m1.destroy()
    await runner.run_for(1)

    assert u.len('mine') == 0
    assert len(radar) == 2


@pytest.mark.asyncio
async def test_autodestruction():
    logger = MessageLogger()
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 20])
    radar = RadarLogger(u)
    v2.send = logger.log

    await runner.run_for(1)
    await v1.onMsg_autodestruction({})
    await runner.run_for(1)

    assert u.len('vessel') == 1

    assert len(radar) == 1
    assert radar[0] == { 'what': 'explosion', 'position': [30, 10]}
    assert len(logger) == 2
    assert logger[-1] == { 'type': 'passive_scan', 'what': 'explosion', 'position': [30, 10]}


@pytest.mark.asyncio
async def test_autodestruction_two_vessels():
    logger = MessageLogger()
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [0, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [0, 1, 1, 1], [30, 13])
    v3 = Vessel(u, ['T', 3, 'test'], [0, 1, 1, 1], [30, 16])
    m = Mine(u, [30, 8], u.t)
    radar = RadarLogger(u)
    v3.send = logger.log

    await runner.run_for(1)
    await v1.onMsg_autodestruction({})
    await runner.run_for(1)

    assert u.len('vessel') == 1
    assert u.len('mine') == 0

    assert len(radar) == 2
    assert radar[-2] == { 'what': 'explosion', 'position': [30, 10]}
    assert radar[-1] == { 'what': 'explosion', 'position': [30, 8]}
    assert len(logger) == 3
    assert logger[-2] == { 'type': 'passive_scan', 'what': 'explosion', 'position': [30, 10]}
    assert logger[-1] == { 'type': 'passive_scan', 'what': 'explosion', 'position': [30, 8]}


@pytest.mark.asyncio
async def test_move_on_radar():
    logger = MessageLogger()
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [29, 9])
    v2.send = logger.log

    await runner.run_for(1)
    await v1.onMsg_move({'direction': [1, 1]})
    await runner.run_for(1)

    assert len(logger) == 2
    assert logger[-1] == { 'type': 'passive_scan', 'what': 'move', 'vessel': v1.name(), 'movement': [1, 1]}


@pytest.mark.asyncio
async def test_laser_attack():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 5, 1, 1], [20, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 10])
    hp = v2.hp

    await runner.run_for(1)
    await v1.onMsg_fire_laser({'direction': [1, 0]})
    await runner.run_for(1)

    assert v2.hp == hp - 20


@pytest.mark.asyncio
async def test_laser_attack_two_vessels():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 5, 1, 1], [20, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 10])
    v3 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [32, 10])
    hp2 = v2.hp
    hp3 = v3.hp

    await runner.run_for(1)
    await v1.onMsg_fire_laser({'direction': [1, 0]})
    await runner.run_for(1)

    assert v2.hp == hp2 - 20
    assert v3.hp == hp3


@pytest.mark.asyncio
async def test_iem_attack():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    logger = MessageLogger()
    v1 = Vessel(u, ['T', 1, 'test'], [1, 5, 1, 1], [20, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 10])
    v2.send = logger.log


    await runner.run_for(1)
    await v1.onMsg_fire_iem({'direction': [1, 0]})
    await runner.run_for(1)

    assert v2.iemed_until > u.t

    await v2.onMsg_move({'direction': [1, 0]})
    assert logger[-1] == { 'type': 'iem_freeze'}


@pytest.mark.asyncio
async def test_iem_attack_two_vessels():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    l2 = MessageLogger()
    l3 = MessageLogger()
    v1 = Vessel(u, ['T', 1, 'test'], [1, 5, 1, 1], [20, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 10])
    v3 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [32, 10])
    v2.send = l2.log
    v3.send = l3.log

    await runner.run_for(1)
    await v1.onMsg_fire_iem({'direction': [1, 0]})
    await runner.run_for(1)

    assert v2.iemed_until > u.t
    assert v3.iemed_until > u.t
    await v2.onMsg_move({'direction': [1, 0]})
    await v3.onMsg_move({'direction': [1, 0]})
    assert l2[-1] == { 'type': 'iem_freeze'}
    assert l3[-1] == { 'type': 'iem_freeze'}
