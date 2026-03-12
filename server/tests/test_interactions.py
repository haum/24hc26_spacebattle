import pytest

from main import set_sender, route_message
from game.asteroid import Asteroid
from game.mine import Mine
from game.torpedo import Torpedo
from game.universe import Universe
from game.vessel import Vessel
from game.resource import Resource

from .utils import UniverseRunner, RadarLogger, MessageLogger


@pytest.mark.asyncio
async def test_torpedo_death():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    Torpedo(u, [10, 10], [-5, 0], u.t+1)
    radar = RadarLogger(u)

    await runner.run_for(3)

    assert u.len('torpedo') == 0


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
async def test_vessel_attacking_vessel_with_torpedo():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [40, 10])
    radar = RadarLogger(u)

    hp1 = v1.hp
    hp2 = v2.hp

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'fire_torpedo', 'direction': [1, 0]})
    await runner.run_for(1)

    assert u.len('torpedo') == 0
    assert u.len('vessel') == 2

    assert v1.hp == hp1
    assert v2.hp == hp2 - 20

    assert len(radar) == 1
    assert radar[0] == { 'what': 'explosion', 'position': [40, 10] }


@pytest.mark.asyncio
async def test_vessels_collision():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [27, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [31, 10])
    radar = RadarLogger(u)

    hp1 = v1.hp
    hp2 = v2.hp

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'move', 'direction': [5, 0]})
    await runner.run_for(3)

    assert v1.hp == hp1 - 15
    assert v2.hp == hp2 - 15

    assert len(radar) == 3
    assert radar[1] == { 'what': 'explosion', 'position': [31, 10]}
    assert radar[2] == { 'what': 'explosion', 'position': [30, 10]}

    assert v1.position == [30, 10]
    assert v2.position == [31, 10]


@pytest.mark.asyncio
async def test_vessel_collision_with_asteroid():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    Asteroid(u, [29, 10])

    hp = v1.hp

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'move', 'direction': [-1, 0]})
    await runner.run_for(3)

    assert u.len('vessel') == 0


@pytest.mark.asyncio
async def test_vessel_collision_with_mine():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    Mine(u, [29, 10], u.t)

    hp = v1.hp

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'move', 'direction': [-1, 0]})
    await runner.run_for(3)

    assert u.len('mine') == 0
    assert v1.hp == hp - 20


@pytest.mark.asyncio
async def test_destroy_vessels_through_mines():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    Torpedo(u, [20, 10], [2, 0], u.t+2)
    m1 = Mine(u, [30, 10], u.t)
    m2 = Mine(u, [34, 10], u.t)
    m3 = Mine(u, [38, 10], u.t)
    m4 = Mine(u, [38, 14], u.t)
    v1 = Vessel(u, ['T', 1, 'test'], [0, 1, 1, 1], [30, 14])
    v2 = Vessel(u, ['T', 2, 'test'], [0, 1, 1, 1], [38, 16])
    v3 = Vessel(u, ['T', 3, 'test'], [0, 1, 1, 1], [10, 10])
    radar = RadarLogger(u)

    await runner.run_for(1)

    assert u.len('mine') == 0
    assert u.len('vessel') == 1
    assert len(radar) == 4


@pytest.mark.asyncio
async def test_vessel_drop_mine():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    radar = RadarLogger(u)

    await runner.run_for(1)
    await route_message(v, None, {'type': 'drop_mine', 'delay': 0.1})
    await route_message(v, None, {'type': 'move', 'direction': [1, 0]})
    await runner.run_for(1)

    assert u.len('mine') == 1
    assert u.len('vessel') == 1
    assert list(u.iter('mine'))[0].position == [30, 10]
    assert len(radar) == 1


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
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 20])
    radar = RadarLogger(u)

    l2 = MessageLogger()
    await set_sender(v2, l2.log)

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'autodestruction'})
    await runner.run_for(1)

    assert u.len('vessel') == 1

    assert len(radar) == 1
    assert radar[0] == { 'what': 'explosion', 'position': [30, 10]}
    assert len(l2) == 2
    assert l2[-1] == { 'type': 'passive_scan', 'what': 'explosion', 'position': [0, -10]}


@pytest.mark.asyncio
async def test_autodestruction_two_vessels():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [0, 1, 1, 1], [30, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [0, 1, 1, 1], [30, 13])
    v3 = Vessel(u, ['T', 3, 'test'], [0, 1, 1, 1], [30, 16])
    m = Mine(u, [30, 8], u.t)
    radar = RadarLogger(u)

    l3 = MessageLogger()
    await set_sender(v3, l3.log)

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'autodestruction'})
    await runner.run_for(1)

    assert u.len('vessel') == 1
    assert u.len('mine') == 0

    assert len(radar) == 2
    assert radar[-2] == { 'what': 'explosion', 'position': [30, 10]}
    assert radar[-1] == { 'what': 'explosion', 'position': [30, 8]}
    assert len(l3) == 3
    assert l3[-2] == { 'type': 'passive_scan', 'what': 'explosion', 'position': [0, -6]}
    assert l3[-1] == { 'type': 'passive_scan', 'what': 'explosion', 'position': [0, -8]}


@pytest.mark.asyncio
async def test_move_on_radar():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [48, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [45, 9])

    l2 = MessageLogger()
    await set_sender(v2, l2.log)

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'move', 'direction': [1, 1]})
    await runner.run_for(1)
    await route_message(v1, None, {'type': 'move', 'direction': [1, 1]})
    await runner.run_for(1)

    assert len(l2) == 3
    assert l2[-2] == { 'type': 'passive_scan', 'what': 'move', 'vessel': v1.name(), 'movement': [1, 1]}
    assert l2[-1] == { 'type': 'passive_scan', 'what': 'move', 'vessel': v1.name(), 'movement': [1, 1]}


@pytest.mark.asyncio
async def test_laser_attack():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 5, 1, 1], [20, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 10])
    hp = v2.hp

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'fire_laser', 'direction': [1, 0]})
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
    await route_message(v1, None, {'type': 'fire_laser', 'direction': [1, 0]})
    await runner.run_for(1)

    assert v2.hp == hp2 - 20
    assert v3.hp == hp3


@pytest.mark.asyncio
async def test_laser_attacking_vessel_behind_asteroid():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 9, 1, 1], [0, 30])
    Asteroid(u, [0, 20])
    radar = RadarLogger(u)

    hp1 = v1.hp

    await runner.run_for(1)
    await route_message(v2, None, {'type': 'fire_laser', 'direction': [0, -1]})
    await runner.run_for(1)

    assert u.len('asteroid') == 1
    assert u.len('vessel') == 2

    assert v1.hp == hp1

    assert len(radar) == 0


@pytest.mark.asyncio
async def test_laser_attacking_vessel_behind_farmable():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 9, 1, 1], [0, 30])
    Resource(u, [0, 20], 10)
    radar = RadarLogger(u)

    hp1 = v1.hp

    await runner.run_for(1)
    await route_message(v2, None, {'type': 'fire_laser', 'direction': [0, -1]})
    await runner.run_for(1)

    assert u.len('farmable') == 1
    assert u.len('vessel') == 2

    assert v1.hp == hp1

    assert len(radar) == 0


@pytest.mark.asyncio
async def test_laser_attacking_vessel_behind_mine():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 9, 1, 1], [0, 30])
    Mine(u, [0, 20], u.t)
    radar = RadarLogger(u)

    hp1 = v1.hp

    await runner.run_for(1)
    await route_message(v2, None, {'type': 'fire_laser', 'direction': [0, -1]})
    await runner.run_for(1)

    assert u.len('mine') == 0
    assert u.len('vessel') == 2

    assert v1.hp == hp1

    assert len(radar) == 1

@pytest.mark.asyncio
async def test_laser_attacking_vessel_behind_mine_close():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 16])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 9, 1, 1], [0, 30])
    Mine(u, [0, 20], u.t)
    radar = RadarLogger(u)

    hp1 = v1.hp

    await runner.run_for(1)
    await route_message(v2, None, {'type': 'fire_laser', 'direction': [0, -1]})
    await runner.run_for(1)

    assert u.len('mine') == 0
    assert u.len('vessel') == 2

    assert v1.hp == hp1 - 20

    assert len(radar) == 1


@pytest.mark.asyncio
async def test_iem_attack():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 5, 1, 1], [20, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 10])

    l2 = MessageLogger()
    await set_sender(v2, l2.log)

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'fire_iem', 'direction': [1, 0]})
    await runner.run_for(1)

    assert v2.iemed_until > u.t

    await route_message(v2, l2.log, {'type': 'move', 'direction': [1, 0]})
    assert l2[-1] == { 'type': 'iem_freeze'}


@pytest.mark.asyncio
async def test_iem_attack_two_vessels():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 5, 1, 1], [20, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 10])
    v3 = Vessel(u, ['T', 3, 'test'], [1, 1, 1, 1], [32, 10])

    l2 = MessageLogger()
    await set_sender(v2, l2.log)
    l3 = MessageLogger()
    await set_sender(v3, l3.log)

    await runner.run_for(1)
    await route_message(v1, None, {'type': 'fire_iem', 'direction': [1, 0]})
    await runner.run_for(1)

    assert v2.iemed_until > u.t
    assert v3.iemed_until > u.t
    await route_message(v2, l2.log, {'type': 'move', 'direction': [1, 0]})
    await route_message(v3, l3.log, {'type': 'move', 'direction': [1, 0]})
    assert l2[-1] == { 'type': 'iem_freeze'}
    assert l3[-1] == { 'type': 'iem_freeze'}

@pytest.mark.asyncio
async def test_active_scan():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 3], [20, 10])
    v2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 10])
    m = Mine(u, [20, 20], u.t)
    r = Torpedo(u, [12, 0], [0, 1], u.t+10)
    a = Asteroid(u, [20, 0])

    l1 = MessageLogger()
    await set_sender(v1, l1.log)

    await runner.run_for(1)
    await route_message(v1, l1.log, {'type': 'scan_radar'})
    await runner.run_for(1)

    assert { 'type': 'active_scan', 'what': 'vessel', 'position': [10, 0]} in l1.messages
    assert { 'type': 'active_scan', 'what': 'mine', 'position': [0, 10]} in l1.messages
    assert { 'type': 'active_scan', 'what': 'torpedo', 'position': [-8, 0]} in l1.messages
    assert { 'type': 'active_scan', 'what': 'asteroid', 'position': [0, -10]} in l1.messages
