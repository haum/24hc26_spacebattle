async def emit_event(u, e):
    for s in u.iter('radar'):
        await s.onPassiveScan(e)


async def emit_explosion(u, o):
    await emit_event(u, {
        'type': 'explosion',
        'position': o.position,
    })

