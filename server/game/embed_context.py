import asyncio

from .game import random_position, randomstr, teams_in_universe
from .asteroid import Asteroid
from .mine import Mine
from .observer import Observer
from .torpedo import Torpedo
from .universe import Universe
from .vector import vector
from .vessel import Vessel

def run_tests():
    import subprocess
    subprocess.run(["pytest", "-v"])


print_teams_task = None
def print_teams(u, dt):
    global print_teams_task
    print_teams_task = asyncio.create_task(print_teams_task_run(u, dt))

async def print_teams_task_run(u, dt):
    while True:
        await asyncio.sleep(dt)
        for v in u.iter('vessel'):
            print(str(v))

def stop_print_teams():
    global print_teams_task
    if print_teams_task:
        print_teams_task.cancel()
        print_teams_task = None
