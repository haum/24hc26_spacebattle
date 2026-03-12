import pytest

from main import set_sender, route_message
from game.universe import Universe
from game.vessel import Vessel

from .utils import UniverseRunner, MessageLogger


@pytest.mark.asyncio
async def test_out_of_energy():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])

    logger = MessageLogger()
    await set_sender(v, logger.log)

    await runner.run_for(1)

    v.energy = 0
    await route_message(v, logger.log, {'type': 'move', 'direction': [1, 1]})

    assert logger[-1] == {'type': 'low_energy'}

