import os

from dotenv import load_dotenv

load_dotenv()

config = {
    'server_host': os.environ.get('SERVER_HOST', '127.0.0.1'),
    'server_port': os.environ.get('SERVER_PORT', 8000),
    'proxy_port': os.environ.get('PROXY_PORT', 8001),
    'server_token': os.environ.get('SERVER_TOKEN'),
    'proxy_token': os.environ.get('PROXY_TOKEN')
}
