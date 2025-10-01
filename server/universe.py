import weakref


class Universe:
    def __init__(self, game):
        self.g = weakref.proxy(game)
        self.objects = set()
        self.lobby = True

    def remove_vessel(self, vessel):
        self.objects.remove(vessel)
        self.g.remove_vessel(vessel)
