import weakref

from .vector import vector, hypervoxels_line
from .radar import emit_explosion

class Mine:
    def __init__(self, universe, position, enabled_time, emitter=None):
        self.u = universe
        self.emitter = weakref.ref(emitter) if emitter else lambda: None
        self.position = position
        self.enabled_time = enabled_time
        self.u.add(self, ['mine', 'collidable'])

    async def destroy(self):
        await emit_explosion(self.u, self)
        self.u.remove(self)
        objects_within_range = (o
            for o in self.u.iter('collidable', self)
            if vector.norm(vector.mod_relative(
                vector.sub(o.position, self.position),
                self.u.size
            )) < 5
        )
        for o in objects_within_range:
            cls = o.__class__.__name__
            if cls == 'Vessel':
                await o.damage(20)
            if cls == 'Mine':
                await o.destroy()

    def __str__(self):
        return f'Mine(p={self.position})'
