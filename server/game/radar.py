async def emit_event(u, e):
    for s in u.iter('radar'):
        await s.onPassiveScan(e)


async def emit_explosion(u, o):
    await emit_event(u, {
        'what': 'explosion',
        'position': o.position,
    })


async def emit_move(u, position, vessel_name, move):
    await emit_event(u, {
        'what': 'move',
        'position': position,
        'vessel': vessel_name,
        'movement': move
    })
