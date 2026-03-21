import asyncio
import functools
import weakref
import math
import random
import string
import time
import json

from .universe import Universe
from .asteroid import Asteroid
from .resource import Resource
from .vessel import Vessel
from .observer import Observer


LOGS = './logs'

def randomstr(k):
    return ''.join(random.choices(string.ascii_letters, k=k))


def random_position(u):
    for _ in range(20):
        p = [random.randint(0, b-1) for b in u.size]
        if all(
            c.position != p
            for c in u.iter('collidable')
        ):
            return p
    return p  # Need to be more clever here


def admin_only(f):
    @functools.wraps(f)
    async def wrapper(game, data):
        if data.get('key', None) != game.get_key('admin'):
            return 'Invalid admin key'
        return await f(game, data)
    return wrapper


def teams_in_universe(u):
    return set(v.hname[0] for v in u.iter('vessel'))


def start_lobby_helper(game, lobby):
    if lobby is game.lobby and len(teams_in_universe(lobby)) > 1:
        game.new_universe(game.lobby.size)


def can_join_tournament(lobby, team):
    required = lobby.required_teams
    teams_present = teams_in_universe(lobby)
    named = {t for t in required if t is not None}
    if team in teams_present or team in named:
        return True
    if None in required:
        wildcard_count = required.count(None)
        wildcard_taken = len(teams_present - named)
        return team not in named and wildcard_taken < wildcard_count
    return False


def tournament_ready(lobby):
    required = lobby.required_teams
    teams_present = teams_in_universe(lobby)
    named = {t for t in required if t is not None}
    if not named.issubset(teams_present):
        return False
    return len(teams_present - named) >= required.count(None)


class Game:
    def __init__(self):
        self.lobby = Universe(randomstr(5), 2)
        self.universes = set()
        self.vessels = weakref.WeakValueDictionary()
        self.tasks = set()
        self.tournament_lobbies = []

        try:
            with open("keys.json", "r") as f:
                self.keys = json.load(f)
        except FileNotFoundError:
            self.keys = {}

    async def destroy_vessels_of_team(self, team):
        for k in list(self.vessels.keys()):
            if self.vessels.get(k).hname[0] == team:
                await self.vessels.get(k).destroy()

    def get_key(self, team_name):
        return self.keys.get(team_name, {}).get('key', None)

    def get_universe(self, name):
        m = list(u for u in self.universes if u.name == name)
        if m:
            return m[0]
        m = list(u for u in self.tournament_lobbies if u.name == name)
        if m:
            return m[0]
        if self.lobby.name == name or name == '':
            return self.lobby
        if name[0] == 'T':
            try:
                return list(self.tournament_lobbies)[int(name[1:])]
            except IndexError:
                return None
            except ValueError:
                return None
        try:
            return list(self.universes)[int(name)]
        except IndexError:
            return None
        except ValueError:
            return None

    def new_universe(self, sz):
        if self.lobby and self.lobby.len('vessel') > 0:
            self.universes.add(self.lobby)
            self.tasks.add(asyncio.create_task(
                self.universe_update_task(self.lobby)
            ))
        self.lobby = Universe(randomstr(5), sz)

    def add_in_lobby(self, team, vessels_stats, universe=None):
        u = universe or self.lobby
        ret = []
        for i, stats in enumerate(vessels_stats):
            p = random_position(u)
            v = Vessel(
                weakref.proxy(u),
                [team, i+1, randomstr(5)],
                stats,
                p
            )
            secret_name = v.name(True)
            self.vessels[secret_name] = v
            ret.append(secret_name)
        return ret

    async def universe_update_task(self, u):
        try:
            for _ in range(min(int(math.prod(u.size)/100), 5000)):
                p = random_position(u)
                Asteroid(u, p)
            for _ in range(min(int(math.prod(u.size)/1000), 100)):
                p = random_position(u)
                Resource(u, p, 500)
            for v in u.iter('vessel'):
                await v.start()
            t0 = time.time()
            lt = 0
            while len(teams_in_universe(u)) > 1:
                u.t = time.time()-t0
                for o in u.iter('update'):
                    await o.onUpdate(u.t-lt, u.t)
                lt = u.t
                delay = t0 + u.t + 0.1 - time.time()
                if delay > 0:
                    await asyncio.sleep(delay)
        except Exception:
            import traceback
            traceback.print_exc(file=traceback.sys.stderr)

        for o in u.iter('observer'):
            await o.onEndOfUniverse()
        won = len(teams_in_universe(u)) == 1
        for v in u.iter('vessel'):
            await v.send([
                {'type': 'won' if won else 'end'},
                'End of game'
            ])
        u.clean()
        self.universes.remove(u)
        self.tasks = {t for t in self.tasks if not t.done()}

    async def onMsg_start(self, data):
        if self.keys and data.get('key', '') != self.get_key(data['team']):
            return 'Invalid key'
        msg = {'type': 'new_vessels'}
        await self.destroy_vessels_of_team(data['team'])

        tlobby = next((l for l in self.tournament_lobbies
                       if can_join_tournament(l, data['team'])), None)
        if tlobby:
            msg['vessels'] = self.add_in_lobby(data['team'], data['vessels'], tlobby)
            if tournament_ready(tlobby):
                self.tournament_lobbies.remove(tlobby)
                self.universes.add(tlobby)
                self.tasks.add(asyncio.create_task(self.universe_update_task(tlobby)))
        else:
            msg['vessels'] = self.add_in_lobby(data['team'], data['vessels'])
            if len(teams_in_universe(self.lobby)) > 1:
                loop = asyncio.get_event_loop()
                loop.call_later(5, start_lobby_helper, self, self.lobby)
        return msg

    async def onMsg_connect(self, data):
        if self.keys and data.get('key', '') != self.get_key(data.get('id', '').split(':')[0]):
            return 'Invalid key'
        if data.get('id', None) in self.vessels:
            return weakref.ref(self.vessels.get(data['id']))
        else:
            return 'Invalid connect'

    @admin_only
    async def onMsg_rq_world_report(self, data):
        if u := self.get_universe(data.get('universe')):
            o = Observer(u)
            return weakref.ref(o)
        return 'Unknown universe'

    @admin_only
    async def onMsg_config_universe(self, data):
        self.new_universe(data['size'])

    @admin_only
    async def onMsg_tournament(self, data):
        lobby_name = randomstr(5)
        lobby = Universe(
            lobby_name, self.lobby.size,
            logfile=f'{LOGS}/tournament_{lobby_name}_{time.strftime('%H%M%S', time.gmtime())}.log')
        lobby.required_teams = data['teams']
        self.tournament_lobbies.append(lobby)
        return {'type': 'tournament_created', 'name': lobby.name}

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'

    def __str__(self):
        s = str(self.lobby)
        for u in self.universes:
            s += '\n'+str(u)
        return s
