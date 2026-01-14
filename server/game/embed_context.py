from .game import random_position, randomstr, teams_in_universe
from .asteroid import Asteroid
from .mine import Mine
from .observer import Observer
from .torpedo import Torpedo
from .universe import Universe
from .vector import vector
from .vessel import Vessel

def run_tests():
    import pytest
    return pytest.main(["-v", "tests"])
