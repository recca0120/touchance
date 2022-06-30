import base64
import hashlib
import urllib.parse
from typing import Union


def urlsafe_base64_encode(hashed: str):
    stripped = hashed.split("=")[0]
    filtered = stripped.replace("+", "-").replace("/", "_")

    return filtered


def urlsafe_base64_decode(hashed: str):
    filtered = hashed.replace("-", "+").replace("_", "/")
    padded = filtered + "=" * ((len(filtered) * -1) % 4)

    return padded


def make_hash(plain_text: str):
    hashed = hashlib.sha256(plain_text.encode('utf-8')).digest()

    return urlsafe_base64_encode(base64.encodebytes(hashed).decode('utf-8').strip())


def get_query_param(path, key) -> Union[str, bytes, None]:
    query = urllib.parse.urlparse(path).query
    params = urllib.parse.parse_qs(query)
    values = params.get(key, [])
    if len(values) == 1:
        return values[0]
