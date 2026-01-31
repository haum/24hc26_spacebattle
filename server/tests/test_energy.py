import pytest

from game.asteroid import Asteroid
from game.mine import Mine
from game.torpedo import Torpedo
from game.universe import Universe
from game.vessel import Vessel

from .utils import MessageLogger, run_universe


@pytest.mark.asyncio
async def test_out_of_energy():
    logger = MessageLogger()
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    v.send = logger.log

    await run_universe(u, 1)
    v.energy = 0
    await v.onMsg_move({'direction': [1, 1]})

    assert logger[-1] == {'type': 'low_energy'}

