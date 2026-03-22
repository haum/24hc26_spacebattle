import asyncio
from .vector import vector

class Notifyer:
    def __init__(self, universe):
        self.u = universe
        self.n = 2
        self.u.add(self, ['update'])

    async def onUpdate(self, _dt, t):
        if t > self.n * 5*60:
            self.n += 1

            for va in self.u.iter('vessel'):
                for vb in self.u.iter('vessel', va):
                    p = vector.mod_relative(
                        vector.sub(vb.position, va.position),
                        self.u.size
                    )
                    await va.send({
                        'type': 'apocalypse',
                        'vessel': vb.name(),
                        'position': p,
                    })

