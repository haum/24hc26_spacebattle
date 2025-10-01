from const import MAX_RESOURCES, MAX_VESSELS, MAX_STAT, STAT_SZ
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
        self.vessels = {
            'sIjdR': Vessel(self),
            'hsUje': Vessel(self),
            'Wjdol': Vessel(self),
            'ppdOd': Vessel(self),
            'NnsgT': Vessel(self),
        }

    async def onMsg_start(self, data):
        msg = {'type': 'new_vessels'}
        if error := validate_start_msg(data):
            return error
        # TODO Do something with the message
        return msg

    async def onUnknownMsg(self, data):
        return 'Unknown message'
