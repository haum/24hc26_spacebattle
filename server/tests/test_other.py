import pytest

from main import set_sender, route_message
from game.game import Game, teams_in_universe
from game.universe import Universe
from game.vessel import Vessel

from .utils import UniverseRunner, MessageLogger


@pytest.mark.asyncio
async def test_ping_game():
    g = Game()
    l = MessageLogger()

    await route_message(g, l.log, {'type': 'ping'})
    await route_message(g, l.log, {'type': 'ping', 'n': 1})
    await route_message(g, l.log, {'type': 'ping', 'n': '4'})

    assert l[0] == {'type': 'pong', 'n': None}
    assert l[1] == {'type': 'pong', 'n': 1}
    assert l[2] == {'type': 'pong', 'n': '4'}


@pytest.mark.asyncio
async def test_ping_vessel():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [40, 10])
    l = MessageLogger()

    await route_message(v, l.log, {'type': 'ping'})
    await route_message(v, l.log, {'type': 'ping', 'n': 1})
    await route_message(v, l.log, {'type': 'ping', 'n': '4'})

    assert l[0] == {'type': 'pong', 'n': None}
    assert l[1] == {'type': 'pong', 'n': 1}
    assert l[2] == {'type': 'pong', 'n': '4'}


@pytest.mark.asyncio
async def test_unknown_game():
    g = Game()
    l = MessageLogger()

    await route_message(g, l.log, {'type': 'djzkdp'})
    assert l[-2] == {'type': 'invalid_msg', 'errors': ['Invalid type']}
    assert l[-1] == 'Invalid message'

    await route_message(g, l.log, {'type': 'fire_iem', 'direction': [0, 1]})
    assert l[-1] == 'Unknown message'

@pytest.mark.asyncio
async def test_unknown_vessel():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [40, 10])
    l = MessageLogger()

    await route_message(v, l.log, {'type': 'djzkdp'})
    assert l[-2] == {'type': 'invalid_msg', 'errors': ['Invalid type']}
    assert l[-1] == 'Invalid message'

    await route_message(v, l.log, {'type': 'start', 'team': 'ZZZ', 'vessels': [[1, 2, 3, 4]]})
    assert l[-1] == 'Unknown message'


@pytest.mark.asyncio
async def test_battle_not_started():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [40, 10])
    l = MessageLogger()

    await route_message(v, l.log, {'type': 'move', 'direction': [0, 1]})
    assert l[-1] == 'Battle not started'

    await route_message(v, l.log, {'type': 'fire_torpedo', 'direction': [0, 1]})
    assert l[-1] == 'Battle not started'

    await route_message(v, l.log, {'type': 'drop_mine'})
    assert l[-1] == 'Battle not started'

    await route_message(v, l.log, {'type': 'fire_laser', 'direction': [0, 1]})
    assert l[-1] == 'Battle not started'

    await route_message(v, l.log, {'type': 'fire_iem', 'direction': [0, 1]})
    assert l[-1] == 'Battle not started'

    await route_message(v, l.log, {'type': 'scan_radar'})
    assert l[-1] == 'Battle not started'

    await route_message(v, l.log, {'type': 'autodestruction'})
    assert l[-1] == 'Battle not started'

    assert len(l) == 7


@pytest.mark.asyncio
async def test_connect_vessel():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [40, 10])

    l = MessageLogger()
    await set_sender(v, l.log)

    await route_message(v, l.log, {'type': 'connect', 'id': 'T:1:wrong'})
    assert l[-1] == 'Connected to another vessel'

    await route_message(v, l.log, {'type': 'connect', 'id': 'T:1:test'})
    assert l[-1] == {'type': 'stats', 'hp': 21, 'stats': [1, 1, 1, 1]}

    await runner.run_for(1)
    assert l[-1] == {'type': 'start_battle'}

    await route_message(v, l.log, {'type': 'connect', 'id': 'T:1:test'})
    assert l[-2] == {'type': 'stats', 'hp': 21, 'stats': [1, 1, 1, 1]}
    assert l[-1] == {'type': 'start_battle'}

    assert len(l) == 5


@pytest.mark.asyncio
async def test_teams_in_universe():
    u = Universe('test', [50, 50])
    vt1 = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [40, 10])
    vt2 = Vessel(u, ['T', 2, 'test'], [1, 1, 1, 1], [30, 10])
    vu1 = Vessel(u, ['U', 1, 'test'], [1, 1, 1, 1], [20, 10])
    assert teams_in_universe(u) == {'T', 'U'}


@pytest.mark.asyncio
async def test_universe_misc():
    u = Universe('test', [50, 50])

    class O:
        def __init__(self, i):
            self.i = i
        def __str__(self):
            return str(self.i)

    V4 = O(4)
    V44 = O(44)
    V3 = O(3)

    u.add(V4, ['number', 'four'])
    u.add(V44, ['number', 'four'])
    u.add(V3, ['number', 'three'])

    assert u.len('number') == 3
    assert u.len('four') == 2
    assert u.len('three') == 1

    u.remove(V3, ['three'])
    u.remove(V4)

    assert u.len('number') == 2
    assert u.len('four') == 1
    assert u.len('three') == 0

    assert set(u.iter('number')) == {V44, V3}
    assert set(u.iter('four')) == {V44,}

    u.clean()

    assert u.len('number') == 0
    assert u.len('four') == 0
    assert u.len('three') == 0
