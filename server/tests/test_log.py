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
async def test_log():
    u = Universe('test', [50, 50], logfile='/tmp/test_log.log')
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [40, 10])

    await route_message(v, None, {'type': 'move', 'direction': [1, 0]})
    await runner.run_for(1)
    await route_message(v, None, {'type': 'drop_mine', 'delay': 0.1})
    await runner.run_for(1)
    await route_message(v, None, {'type': 'fire_torpedo', 'direction': [2,3]})
    await runner.run_for(1)
    await route_message(v, None, {'type': 'fire_iem', 'direction': [2,3]})
    await runner.run_for(1)
    await route_message(v, None, {'type': 'fire_laser', 'direction': [1,0]})
    await runner.run_for(1)
    await route_message(v, None, {'type': 'autodestruction'})
    await runner.run_for(1)

    u.clean()







