from vessel import Vessel


class Game:
    def __init__(self):
        self.vessels = {
            'sIjdR': Vessel(self),
            'hsUje': Vessel(self),
            'Wjdol': Vessel(self),
            'ppdOd': Vessel(self),
            'NnsgT': Vessel(self),
        }

    async def onUnknownMsg(self, data):
        return 'Unknown message'
