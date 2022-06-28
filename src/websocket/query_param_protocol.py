import http

from websockets.legacy.server import WebSocketServerProtocol

from src.websocket.utils import get_query_param, urlsafe_base64_encode


def access_token():
    return 'Tn1pa86JRUjd7XL27rBOjWJcx_Kv0IhFgkpKg3i0KNE'


class QueryParamProtocol(WebSocketServerProtocol):
    async def process_request(self, path, headers):
        token = get_query_param(path, 'token')
        if token is None or urlsafe_base64_encode(token) != access_token():
            return http.HTTPStatus.UNAUTHORIZED, [], b"Invalid token\n"
