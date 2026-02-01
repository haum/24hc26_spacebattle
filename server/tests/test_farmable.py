import pytest

from game.resource import Resource
from game.universe import Universe
from game.vessel import Vessel, HP_LUT

from .utils import MessageLogger, run_universe


@pytest.mark.asyncio
async def test_harvest_regular():
    logger = MessageLogger()
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    r = Resource(u, [0, 10], 40)
    v.send = logger.log
    v.energy = 0

    await run_universe(u, 1)

    assert r.quantity == 20
    assert v.energy == 20+10 # harvested 20 + 10 regen


@pytest.mark.asyncio
async def test_harvest_finish():
    logger = MessageLogger()
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    r = Resource(u, [0, 10], 20)
    v.send = logger.log
    v.energy = 0

    await run_universe(u, 1)

    assert r.quantity == 0
    assert v.energy == 20+10 # harvested 20 + 10 regen
    assert logger.messages[-1] == {'type': 'resource_depleted'}
    assert r not in u.objects


@pytest.mark.asyncio
async def test_harvest_partial():
    logger = MessageLogger()
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    r = Resource(u, [0, 10], 9)
    v.send = logger.log
    v.energy = 0

    await run_universe(u, 1)

    assert r.quantity == 0
    assert v.energy == 9+10 # harvested 9 + 10 regen
    assert logger.messages[-1] == {'type': 'resource_depleted'}
    assert r not in u.objects


@pytest.mark.asyncio
async def test_destroy_to_farmable():
    logger = MessageLogger()
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    v.send = logger.log

    await v.destroy()

    r = (u.iter('farmable')).__next__()
    assert r.quantity == HP_LUT[1]
    assert r.position == v.position
    assert r.rate == 5
    assert logger.messages[-2] == 'Vessel destroyed'
