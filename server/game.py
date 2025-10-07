from const import MAX_RESOURCES, MAX_VESSELS, MAX_STAT, STAT_SZ
from universe import Universe
from vessel import Vessel


def validate_start_msg(data):
    msgerror = 'Invalid start: '
    if 'team' not in data:
        return msgerror + 'unknown team'
    if not isinstance(data['team'], str):
        return msgerror + 'invalid team'
    if 'vessels' not in data:
        return msgerror + 'unknown vessels'
    vessels = data.get('vessels')
    if not isinstance(vessels, list):
        return msgerror + 'invalid vessels'
    if not 0 < len(vessels) <= MAX_VESSELS:
        return msgerror + 'invalid number of vessels'
    if not is_valid_stat_list(vessels):
        return msgerror + 'invalid vessel stats'
    if sum((sum(v) for v in vessels)) > MAX_RESOURCES:
        return msgerror + 'invalid allocation of resources'


def is_valid_stat_list(vessels):
    return all((
        isinstance(v, list) and
        len(v) == STAT_SZ and
        all((
            isinstance(x, int) and
            0 <= x <= MAX_STAT
        ) for x in v)
    ) for v in vessels)


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
        if error := validate_start_msg(data):
            return error
        await self.destroy_vessels_of_team(data['team'])
        msg['vessels'] = self.add_in_lobby(data['team'], data['vessels'])
        return msg

    async def onUnknownMsg(self, data):
        return 'Unknown message'
