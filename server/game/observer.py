import asyncio
import weakref


async def no_send(_):
    pass


class Observer:
    def __init__(self, universe):
        self.u = weakref.proxy(universe)
        self.send = no_send
        self.u.add(self, ['observer'])
        self.delay = 0.1
        self.alive = True

    async def set_sender(self, send):
        await self.send('Disconnected by another pilot')
        self.send = send or no_send

    async def task(self):
        while self.alive:
            try:
                await self.send({
                    'type': 'world_report',
                    'size': self.u.size,
                    'asteroids': [
                        a.position.get()
                        for a in self.u.iter('asteroid')
                    ],
                    'vessels': [
                        (v.name(), v.position.get())
                        for v in self.u.iter('vessel')
                    ],
                    'torpedos': [
                        (
                            t.emitter.name() if t.emitter else '',
                            t.position.get()
                        )
                        for t in self.u.iter('torpedo')
                    ],
                })
                await asyncio.sleep(self.delay)
            except ReferenceError:
                self.alive = False
        self.u.remove(self)

    async def onMsg_rq_world_report(self, data):
        self.delay = max(0.1, data['dt'])
        self.task = asyncio.create_task(self.task())

    async def onMsg_ping(self, data):
        return {'type': 'pong', 'n': data.get('n', None)}

    async def onDisconnect(self):
        self.alive = False

    async def onEndOfUniverse(self):
        await self.send('End of universe')
        self.alive = False

    async def onUnknownMsg(self, data):
        return 'Unknown message'
