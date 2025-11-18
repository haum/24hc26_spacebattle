from universe import Universe
from vessel import Vessel


class Game:
    def __init__(self):
        self.universes = set()
        self.vessels = {}

    def remove_vessel(self, vessel):
        self.vessels.pop(vessel.name())

    async def destroy_vessels_of_team(self, team):
        keys = list(k for k in self.vessels.keys() if k.startswith(team))
        for k in keys:
            await self.vessels.get(k).destroy()

    def add_in_lobby(self, team, vessels_stats):
        ret = []
        u = next(filter(lambda u: u.lobby, self.universes), None)
        if not u:
            u = Universe(self)
            self.universes.add(u)
        for i, stats in enumerate(vessels_stats):
            v = Vessel(self, u, stats)
            name = f'{team}-{i+1}'
            self.vessels[name] = v
            ret.append(name)
            u.objects.add(v)
        return ret

    async def onMsg_start(self, data):
        msg = {'type': 'new_vessels'}
        await self.destroy_vessels_of_team(data['team'])
        msg['vessels'] = self.add_in_lobby(data['team'], data['vessels'])
        return msg

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onUnknownMsg(self, data):
        return 'Unknown message'
