import asyncio
import aiohttp
import aiohttp.web as web
import functools
import json
import os
import weakref
import sys

from msgs import validate_msg
from game import Game


async def index(rq):
    return web.Response(text='24HC26 game server')


def redirect301(url):
    async def impl(rq):
        raise web.HTTPMovedPermanently(url)
    return impl


def static_file(path):
    async def impl(rq):
        subpath = rq.match_info.get('path', None)
        f = f'{path}/{subpath}' if subpath else path
        if not os.path.exists(f):
            raise web.HTTPNotFound()
        if os.path.isdir(f):
            files = os.listdir(f)
            files.sort()
            response = web.Response(
                body=json.dumps(files, indent='\t', sort_keys=True),
                content_type='application/json'
            )
        else:
            response = web.FileResponse(f)
            response.headers['Cache-Control'] = 'max-age=30, must-revalidate'
        return response
    return impl


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
    vessel = lambda: None
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
                        vessel0 = vessel
                        vessel = weakref.ref(vessels.get(data['id']))
                        if vessel0 != vessel:
                            if vessel0() is not None:
                                vessel0().set_sender(None)
                            await vessel().send('Disconnected by another pilot')
                        vessel().send = functools.partial(send_msg, ws)
                        await send_to_obj(ws, vessel(), data)
                    else:
                        await ws.close(message='Invalid connect')
                else:
                    await send_to_obj(ws, vessel() or rq.app['game'], data)

            elif msg.type == aiohttp.WSMsgType.BINARY:
                await ws.close(code=aiohttp.WSCloseCode.UNSUPPORTED_DATA)
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                print(f'ws connection closed: {msg.extra}')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f'ws connection closed with exception: {ws.exception()}')
    finally:
        rq.app['websockets'].discard(ws)
        if vessel():
            vessel().set_sender(None)

    return ws


async def console():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    while await reader.readline():
        print('-----')
        print(app['game'])


async def on_startup(app):
    app['console'] = asyncio.create_task(console())


async def on_shutdown(app):
    for ws in set(app['websockets']):
        await ws.close(
            code=aiohttp.WSCloseCode.GOING_AWAY,
            message='Server shutdown'
        )

app = web.Application()

app['game'] = Game()

app.on_startup.append(on_startup)

app['websockets'] = weakref.WeakSet()
app.on_shutdown.append(on_shutdown)

app.add_routes([
    web.get('/', index),
    web.get('/ws', mainws),
])

for d in []:
    if os.path.isdir(d):
        app.router.add_route('GET', f'/{d}', redirect301(d+'/'))
        app.router.add_route('GET', f'/{d}/', static_file(d+'/index.html'))
        app.router.add_route('GET', f'/{d}/' + '{path:.*}', static_file(d))
    else:
        app.router.add_route('GET', f'/{d}', static_file(d))

web.run_app(app)
