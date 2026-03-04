import pytest

from game.asteroid import Asteroid
from game.mine import Mine
from game.torpedo import Torpedo
from game.universe import Universe
from game.vessel import Vessel
from game.resource import Resource

from .utils import UniverseRunner

def test_vessel_str():
    u = Universe('test', [50, 50])
    v = Vessel(u, ['T', 1, 'test'], [1, 1, 1, 1], [0, 10])

    assert str(v) == "Vessel(p=[0, 10], hp=21, energy=(100), stats=(H:1 A:1 S:1 R:1), hname=(T:1)"


def test_mine_str():
    u = Universe('test', [50, 50])
    m = Mine(u, [5, 5], 0)

    assert str(m) == "Mine(p=[5, 5])"


def test_asteroid_str():
    u = Universe('test', [50, 50])
    a = Asteroid(u, [10, 10])

    assert str(a) == "Asteroid(p=[10, 10])"


@pytest.mark.asyncio
async def test_torpedo_str():
    u = Universe('test', [50, 50])
    runner = UniverseRunner(u)
    t = Torpedo(u, [15, 15], [1, 0], die_time=u.t+2.5)

    assert str(t) == "Torpedo(p=[15, 15], s=[1.0, 0.0], l=2.5)"

    await runner.run_for(1)

    assert str(t) == "Torpedo(p=[25, 15], s=[1.0, 0.0], l=1.6)"


def test_resource_str():
    u = Universe('test', [50, 50])
    r = Resource(u, [20, 20], 100)

    assert str(r) == "Ressource(p=[20, 20], qty=100)"
