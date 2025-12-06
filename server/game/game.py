import asyncio
import functools
import weakref
import random
import string
import time

from game.universe import Universe
from game.vessel import Vessel
from game.observer import Observer


def randomstr(k):
    return ''.join(random.choices(string.ascii_letters, k=k))


def random_position(u):
    for _ in range(20):
        p = [random.randint(0, b-1) for b in u.size]
        if all(
            c.position.get() != p
            for c in u.iter('collidable')
        ):
            return p
    return p  # Need to be more clever here


def admin_only(f):
    @functools.wraps(f)
    async def wrapper(game, data):
        if game.ADMIN_KEY and data.get('key', None) != Game.ADMIN_KEY:
            return 'Invalid admin key'
        return await f(game, data)
    return wrapper


def teams_in_universe(u):
    return set(v.hname[0] for v in u.iter('vessel'))


def start_lobby_helper(game, lobby):
    if lobby is game.lobby and len(teams_in_universe(lobby)) > 1:
        game.new_universe(game.lobby.size)


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
        self.tasks = set()

    async def destroy_vessels_of_team(self, team):
        for k in list(self.vessels.keys()):
            if self.vessels.get(k).hname[0] == team:
                await self.vessels.get(k).destroy()

    def new_universe(self, sz):
        if self.lobby and self.lobby.len('vessel') > 0:
            self.universes.add(self.lobby)
            self.tasks.add(asyncio.create_task(
                self.universe_update_task(self.lobby)
            ))
        self.lobby = Universe(sz)

    def add_in_lobby(self, team, vessels_stats):
        ret = []
        for i, stats in enumerate(vessels_stats):
            p = random_position(self.lobby)
            v = Vessel(
                self.lobby,
                [team, i+1, randomstr(5)],
                stats,
                p
            )
            secret_name = v.name(True)
            self.vessels[secret_name] = v
            ret.append(secret_name)
        return ret

    async def universe_update_task(self, u):
        for v in u.iter('vessel'):
            await v.start()
        t0 = time.time()
        lt = t0
        while len(teams_in_universe(u)) > 1:
            t = time.time()
            for o in u.iter('update'):
                o.onUpdate(t-lt, t-t0)
            lt = t
            await asyncio.sleep(0.1)
        for o in u.iter('observer'):
            await o.onEndOfUniverse()
        for v in u.iter('vessel'):
            await v.send([
                {'type': 'won'},
                'End of game'
            ])
        u.clean()
        self.universes.remove(u)
        self.tasks = {t for t in self.tasks if not t.done()}

    async def onMsg_start(self, data):
        msg = {'type': 'new_vessels'}
        await self.destroy_vessels_of_team(data['team'])
        msg['vessels'] = self.add_in_lobby(data['team'], data['vessels'])
        if len(teams_in_universe(self.lobby)) > 1:
            loop = asyncio.get_event_loop()
            loop.call_later(5, start_lobby_helper, self, self.lobby)
        return msg

    async def onMsg_connect(self, data):
        if data.get('id', None) in self.vessels:
            return weakref.ref(self.vessels.get(data['id']))
        else:
            return 'Invalid connect'

    @admin_only
    async def onMsg_rq_world_report(self, data):
        o = Observer(self.lobby)
        return weakref.ref(o)

    @admin_only
    async def onMsg_config_universe(self, data):
        self.new_universe(data['size'])

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'

    def __str__(self):
        s = str(self.lobby)
        for u in self.universes:
            s += '\n'+str(u)
        return s
