import asyncio
import base64
import hashlib
import http
import re
import signal
import urllib.parse
from typing import Union

import websockets
from websockets.legacy.server import WebSocketServerProtocol


def urlsafe_base64_encode(hashed: str):
    stripped = hashed.split("=")[0]
    filtered = stripped.replace("+", "-").replace("/", "_")

    return filtered


def urlsafe_base64_decode(hashed: str):
    filtered = hashed.replace("-", "+").replace("_", "/")
    padded = filtered + "=" * ((len(filtered) * -1) % 4)

    return padded


def sha256(plain_text: str):
    hashed = hashlib.sha256(plain_text.encode('utf-8')).digest()

    return urlsafe_base64_encode(base64.encodebytes(hashed).decode('utf-8').strip())


def get_query_param(path, key) -> Union[str, bytes, None]:
    query = urllib.parse.urlparse(path).query
    params = urllib.parse.parse_qs(query)
    values = params.get(key, [])
    if len(values) == 1:
        return values[0]


def access_token():
    return ''


class QueryParamProtocol(WebSocketServerProtocol):
    async def process_request(self, path, headers):
        token = get_query_param(path, 'token')
        if token is None or urlsafe_base64_encode(token) != access_token():
            return http.HTTPStatus.UNAUTHORIZED, [], b"Invalid token\n"


async def echo(websocket: WebSocketServerProtocol):
    path = re.sub(r'\?.*$', '', websocket.path).strip('/')
    async for message in websocket:
        await websocket.send(message)


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGINT, stop.set_result, None)
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with websockets.serve(echo, host='', port=8000, create_protocol=QueryParamProtocol):
        await stop


if __name__ == '__main__':
    asyncio.run(main())
