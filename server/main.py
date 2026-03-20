#!/usr/bin/env python3

import asyncio
import aiohttp
import aiohttp.web as web
import functools
import json
import os
import weakref
import sys
import socket

from datetime import datetime, date
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

hostname = socket.gethostname()

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


async def set_sender(obj, reply, ws=None):
    if obj and hasattr(obj, 'set_sender'):
        await obj.set_sender(
            functools.partial(send_replies, reply, ws=ws)
        )


async def send_replies(reply, data, ws=None):
    if isinstance(data, str) or isinstance(data, dict):
        if reply: await reply(data)
    elif isinstance(data, weakref.ReferenceType):
        if ws:
            if ws.msgobj() is not data():
                if ws.msgobj() and hasattr(ws.msgobj(), 'set_sender'):
                    await ws.msgobj().set_sender(None)
                await set_sender(data(), reply, ws)
            ws.msgobj = data
    elif data:
        for o in data:
            await send_replies(reply, o, ws)


def ws_sender(ws):
    async def send(data):
        if isinstance(data, str):
            await ws.close(message=data)
        else:
            await ws.send_json(data)
    return send


async def route_message(obj, reply, data, ws=None):
    invalid = validate_msg(data)
    if invalid:
        await send_replies(reply, [
            {'type': 'invalid_msg', 'errors': invalid},
            'Invalid message'
        ], ws)
        return

    h = getattr(
        obj, f'onMsg_{data['type']}',
        getattr(obj, 'onUnknownMsg', False)
    )
    await send_replies(reply, await h(data) if h else [], ws)

    if ws and obj is not ws.msgobj():
        await route_message(ws.msgobj(), reply, data, ws)


async def mainws(rq):
    ws = web.WebSocketResponse()
    await ws.prepare(rq)

    rq.app[app_key_w].add(ws)
    try:
        ws.msgobj = weakref.ref(rq.app[app_key_g])
        await ws.send_json({'type': 'hello', 'need_keys': bool(ws.msgobj().keys) })
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = msg.json()
                except json.decoder.JSONDecodeError:
                    await ws.close(message='Invalid JSON')
                    continue
                await route_message(ws.msgobj(), ws_sender(ws), data, ws)
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

    for d in ['doc', 'viewer']:
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

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
