#!/usr/bin/env python3

import asyncio
import aiohttp
import aiohttp.web as web
import functools
import json
import os
import weakref
import sys

from messages import validate_msg
from game.game import Game

try:
    import IPython
    import nest_asyncio2
    nest_asyncio2.apply()
except ModuleNotFoundError:
    IPython = None

game = None
http_runner = None
app_key_g = web.AppKey("game", Game)
app_key_w = web.AppKey("websockets", weakref.WeakSet)
app_key_c = web.AppKey("console", asyncio.Task)

hostname = os.environ.get('HOSTNAME')

async def index(rq):
    if hostname == "24hc26" and date(2026,3,21) <= date.today() <= date(2026,3,22):
        return web.FileResponse('./index.html')
    elif hostname != "24hc26":
        return web.FileResponse('./index.html')
    else:
        return web.Response(text='')


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


async def send_to_obj(ws, data):
    h = getattr(ws.msgobj(), f'onMsg_{data['type']}', None)
    if h:
        res = await h(data)
    elif hasattr(ws.msgobj(), 'onUnknownMsg'):
        res = await ws.msgobj().onUnknownMsg(data)

    previous_msgobj = ws.msgobj()
    await send_msg(ws, res)
    if previous_msgobj is not ws.msgobj():
        await send_to_obj(ws, data)


async def send_msg(ws, data):
    if isinstance(data, str):
        await ws.close(message=data)
    elif isinstance(data, dict):
        await ws.send_json(data)
    elif isinstance(data, weakref.ReferenceType):
        if ws.msgobj() is not data():
            if ws.msgobj() and hasattr(ws.msgobj(), 'set_sender'):
                await ws.msgobj().set_sender(None)
            if data() and hasattr(data(), 'set_sender'):
                await data().set_sender(functools.partial(send_msg, ws))
        ws.msgobj = data
    elif data:
        for o in data:
            await send_msg(ws, o)


async def mainws(rq):
    ws = web.WebSocketResponse()
    await ws.prepare(rq)

    rq.app[app_key_w].add(ws)
    try:
        ws.msgobj = weakref.ref(rq.app[app_key_g])
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
                    await send_msg(ws, [
                        {'type': 'invalid_msg', 'errors': inval},
                        'Invalid message'
                    ])
                    continue

                await send_to_obj(ws, data)

            elif msg.type == aiohttp.WSMsgType.BINARY:
                await ws.close(code=aiohttp.WSCloseCode.UNSUPPORTED_DATA)
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                print(f'ws connection closed: {msg.extra}')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f'ws connection closed with exception: {ws.exception()}')
    finally:
        rq.app[app_key_w].discard(ws)
        if ws.msgobj():
            if hasattr(ws.msgobj(), 'onDisconnect'):
                await ws.msgobj().onDisconnect()
            if hasattr(ws.msgobj(), 'set_sender'):
                await ws.msgobj().set_sender(None)

    return ws


async def console():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    while await reader.readline():
        print('-----')
        print(game)


async def on_startup(app):
    if not IPython:
        app[app_key_c] = asyncio.create_task(console())


async def on_shutdown(app):
    for ws in set(app[app_key_w]):
        await ws.close(
            code=aiohttp.WSCloseCode.GOING_AWAY,
            message='Server shutdown'
        )


async def start_server():
    app = web.Application()

    app[app_key_g] = Game()
    app[app_key_w] = weakref.WeakSet()

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    app.add_routes([
        web.get('/', index),
        web.get('/ws', mainws),
    ])

    for d in ['doc', '2dview']:
        if os.path.isdir(d):
            app.router.add_route('GET', f'/{d}', redirect301(d+'/'))
            app.router.add_route('GET', f'/{d}/', static_file(d+'/index.html'))
            app.router.add_route('GET', f'/{d}/' + '{path:.*}', static_file(d))
        else:
            app.router.add_route('GET', f'/{d}', static_file(d))

    global game
    game = app[app_key_g]

    global http_runner
    http_runner = web.AppRunner(app)
    await http_runner.setup()
    site = web.TCPSite(http_runner, "0.0.0.0", 8080)
    await site.start()

    for sock in http_runner.addresses:
        print(''.join([
            '\033[33m',
            'Serving on ',
            '\033[93;1m',
            f'http://{sock[0]}:{sock[1]}/',
            '\033[0m',
        ]))


async def main():
    await start_server()
    this_task = asyncio.current_task()

    if IPython:
        embed_namespace = {
            'game': game,
            'g': type('', (), {'__repr__': lambda _: str(game)})(),
        }

        import importlib
        module = importlib.import_module('game.embed_context')
        for attr in dir(module):
            if not attr.startswith('_'):
                embed_namespace[attr] = getattr(module, attr)

        from traitlets.config import Config
        c = Config()
        c.InteractiveShell.autoawait = True
        c.InteractiveShell.autocall = 1
        c.InteractiveShell.banner1 = ''
        c.InteractiveShell.call_pdb = True
        c.InteractiveShell.enable_tip = False
        c.InteractiveShell.show_rewritten_input = True
        ipshell = IPython.terminal.embed.InteractiveShellEmbed(
            config=c,
            user_ns=embed_namespace,
        )
        ipshell()

        await http_runner.cleanup()
        for task in asyncio.all_tasks():
            if task is not this_task:
                task.cancel()
        await asyncio.sleep(0)
        asyncio.get_event_loop().stop()

    await asyncio.gather(*filter(
        lambda x: x != this_task,
        asyncio.all_tasks()
    ))

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
