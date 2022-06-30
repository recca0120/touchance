import http

from websockets.legacy.server import WebSocketServerProtocol

from config import config
from touchance.websocket.utils import get_query_param, urlsafe_base64_encode


class QueryParamProtocol(WebSocketServerProtocol):
    async def process_request(self, path, headers):
        access_token = config.get('server_token') \
            if self.extra_headers['type'] == 'server' else config.get('proxy_token')

        token = get_query_param(path, 'token')
        if token is None or urlsafe_base64_encode(token) != access_token:
            return http.HTTPStatus.UNAUTHORIZED, [], b"Invalid token\n"
