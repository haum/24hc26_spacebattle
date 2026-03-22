import asyncio
from .vector import vector

class Notifyer:
    def __init__(self, universe, initial_timestamp_mn=2, interval_mn=5):
        self.u = universe
        self.timestamp = initial_timestamp_mn*60
        self.interval = interval_mn*60
        self.u.add(self, ['update'])

    async def onUpdate(self, _dt, t):
        if t > self.timestamp:
            self.timestamp += self.interval

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

