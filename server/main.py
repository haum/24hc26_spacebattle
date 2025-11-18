import aiohttp
import aiohttp.web as web
import functools
import json
import weakref

from msgs import validate_msg
from game import Game


async def index(rq):
    return web.Response(text='24HC26 game server')


async def send_to_obj(ws, obj, data):
    h = getattr(obj, f'onMsg_{data['type']}', None)
    if h:
        res = await h(data)
    else:
        res = await obj.onUnknownMsg(data)
    await send_msg(ws, res)


async def send_msg(ws, data):
    if isinstance(data, str):
        await ws.close(message=data)
    elif isinstance(data, dict):
        await ws.send_json(data)
    elif data:
        for o in data:
            await ws.send_json(o)


async def mainws(rq):
    ws = web.WebSocketResponse()
    await ws.prepare(rq)

    rq.app['websockets'].add(ws)
    vessel = None
    try:
        await ws.send_json({'type': 'hello'})
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = msg.json()
                except json.decoder.JSONDecodeError:
                    await ws.close(message='Invalid JSON')
                    continue

                inval = validate_msg(data)
                if inval:
                    await send_msg(ws, {
                        'type': 'invalid_msg', 'errors': inval
                    })
                    await ws.close(message='Invalid message')
                    continue

                if data['type'] == 'connect':
                    vessels = rq.app['game'].vessels
                    if data.get('id', None) in vessels:
                        vessel = weakref.proxy(vessels.get(data['id']))
                        await vessel.send('Disconnected by another pilot')
                        vessel.send = functools.partial(send_msg, ws)
                        await send_to_obj(ws, vessel, data)
                    else:
                        await ws.close(message='Invalid connect')
                else:
                    await send_to_obj(ws, vessel or rq.app['game'], data)

            elif msg.type == aiohttp.WSMsgType.BINARY:
                await ws.close(code=aiohttp.WSCloseCode.UNSUPPORTED_DATA)
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                print(f'ws connection closed: {msg.extra}')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f'ws connection closed with exception: {ws.exception()}')
    finally:
        rq.app['websockets'].discard(ws)
        if vessel:
            vessel.reset_send()

    return ws


async def on_shutdown(app):
    for ws in set(app['websockets']):
        await ws.close(
            code=aiohttp.WSCloseCode.GOING_AWAY,
            message='Server shutdown'
        )

app = web.Application()

app['game'] = Game()

app['websockets'] = weakref.WeakSet()
app.on_shutdown.append(on_shutdown)

app.add_routes([
    web.get('/', index),
    web.get('/ws', mainws),
])

web.run_app(app)
