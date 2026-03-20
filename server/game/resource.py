class Resource:
    def __init__(self, universe, position, quantity, destroyed_vessel=False):
        self.u = universe
        self.position = position
        self.u.add(self, ['resource'])

        self.quantity = quantity
        self.rate = 5 if destroyed_vessel else 20

    async def destroy(self):
        self.u.remove(self)

    async def harvest(self, _dt):

        harvested = min(self.rate*_dt, self.quantity)
        self.quantity -= harvested
        if self.quantity <= 0:
            await self.destroy()
        return harvested, self.quantity>0

    def __str__(self):
        return f'Ressource(p={self.position}, qty={self.quantity})'

