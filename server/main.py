import aiohttp
import aiohttp.web as web
import json
import weakref

from game import Game


async def index(rq):
    return web.Response(text='24HC26 game server')


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
                    if 'type' not in data:
                        await ws.close(message='Unknown type')
                        continue
                except json.decoder.JSONDecodeError:
                    await ws.close(message='Invalid JSON')
                    continue
                if vessel:
                    h = getattr(vessel, f'onMsg_{data['type']}', None)
                    if h:
                        res = await h(data)
                    else:
                        res = await vessel.onUnknownMsg(data)
                    if res is not None:
                        await ws.close(message=str(res))
                        continue
                else:
                    vessels = rq.app['game'].vessels
                    if (data['type'] != 'connect'
                       or data.get('id', None) not in vessels):
                        await ws.close(message='Invalid connect')
                        continue
                    vessel = weakref.proxy(vessels.get(data['id']))
                    vessel.send = ws.send_json

            elif msg.type == aiohttp.WSMsgType.BINARY:
                await ws.close(code=aiohttp.WSCloseCode.UNSUPPORTED_DATA)
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                print(f'ws connection closed: {msg.extra}')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f'ws connection closed with exception: {ws.exception()}')
    finally:
        rq.app['websockets'].discard(ws)
        if vessel:
            vessel.send = lambda x: None

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
