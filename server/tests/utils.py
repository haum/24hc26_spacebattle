class UniverseRunner:
    def __init__(self, u):
        self.started = False
        self.u = u

    async def start(self):
        self.started = True
        for v in self.u.iter('vessel'):
            await v.start()

    async def run_for(self, duration):
        if not self.started: await self.start()
        u = self.u
        t0 = u.t
        for t in range(duration*10):
            u.t = t0 + t/10
            for o in u.iter('update'):
                await o.onUpdate(0.1, u.t)


class MessageLogger:
    def __init__(self):
        self.messages = []

    async def log(self, message):
        self.messages.append(message)

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, index):
        return self.messages[index]


class RadarLogger(MessageLogger):
    def __init__(self, u):
        super().__init__()
        u.add(self, ['radar'])

    async def onPassiveScan(self, data):
        await self.log(data)


def float_eq(a, b):
    return abs(a-b) < 1e-6
