import functools
import weakref
import random
import string

from universe import Universe
from vessel import Vessel


def randomstr(k):
    return ''.join(random.choices(string.ascii_letters, k=k))


def admin_only(f):
    @functools.wraps(f)
    async def wrapper(game, data):
        if game.ADMIN_KEY and data.get('key', None) != Game.ADMIN_KEY:
            return 'Invalid admin key'
        return await f(game, data)
    return wrapper


class Game:
    try:
        with open("admin_key.txt", "r") as f:
            ADMIN_KEY = f.read().strip()
    except FileNotFoundError:
        ADMIN_KEY = None

    def __init__(self):
        self.lobby = Universe(2)
        self.universes = set()
        self.vessels = weakref.WeakValueDictionary()

    async def destroy_vessels_of_team(self, team):
        keys = list(k for k in self.vessels.keys() if k.startswith(team))
        for k in keys:
            await self.vessels.get(k).destroy()

    def new_universe(self, sz):
        if self.lobby and self.lobby.len('vessel') > 0:
            self.universes.add(self.lobby)
        self.lobby = Universe(sz)

    def add_in_lobby(self, team, vessels_stats):
        ret = []
        for i, stats in enumerate(vessels_stats):
            v = Vessel(
                self.lobby,
                [team, i+1, randomstr(5)],
                stats
            )
            secret_name = v.name(True)
            self.vessels[secret_name] = v
            ret.append(secret_name)
        return ret

    async def onMsg_start(self, data):
        msg = {'type': 'new_vessels'}
        await self.destroy_vessels_of_team(data['team'])
        msg['vessels'] = self.add_in_lobby(data['team'], data['vessels'])
        return msg

    @admin_only
    async def onMsg_config_universe(self, data):
        self.new_universe(data['size'])

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'

    def __str__(self):
        return str(self.lobby)
