async def run_universe(u, duration):
    for v in u.iter('vessel'):
        await v.start()
    for t in range(duration*10):
        u.t = t/10
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
