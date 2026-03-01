import pytest

from game.resource import Resource
from game.universe import Universe
from game.vessel import Vessel, HP_LUT

from .utils import UniverseRunner, MessageLogger


@pytest.mark.asyncio
async def test_harvest_regular():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    r1 = Resource(u, [0, 10], 40)
    r2 = Resource(u, [0, 11], 40)
    v.energy = 0

    logger = MessageLogger()
    v.send = logger.log

    await runner.run_for(1)

    assert r1.quantity == 20
    assert r2.quantity == 40
    assert v.energy == 20+10 # harvested 20 + 10 regen


@pytest.mark.asyncio
async def test_harvest_finish():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    r = Resource(u, [0, 10], 20)
    v.energy = 0

    logger = MessageLogger()
    v.send = logger.log

    await runner.run_for(1)

    assert r.quantity == 0
    assert v.energy == 20+10 # harvested 20 + 10 regen
    assert logger.messages[-1] == {'type': 'resource_depleted'}
    assert r not in u.objects


@pytest.mark.asyncio
async def test_harvest_partial():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])
    r = Resource(u, [0, 10], 9)
    v.energy = 0

    logger = MessageLogger()
    v.send = logger.log

    await runner.run_for(1)

    assert r.quantity == 0
    assert v.energy == 9+10 # harvested 9 + 10 regen
    assert logger.messages[-1] == {'type': 'resource_depleted'}
    assert r not in u.objects


@pytest.mark.asyncio
async def test_destroy_to_farmable():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])

    logger = MessageLogger()
    v.send = logger.log

    await v.destroy()

    assert u.len('farmable') == 1
    r = next(u.iter('farmable'))
    assert r.quantity == HP_LUT[1]
    assert r.position == v.position
    assert r.rate == 5
    assert logger.messages[-2] == 'Vessel destroyed'
