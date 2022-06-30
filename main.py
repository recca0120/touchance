import argparse
import asyncio
import logging
import sys

from config import config
from touchance.websocket.proxy import __start_proxy
from touchance.websocket.server import __start_wss_server

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)

is_win = sys.platform.startswith("win")
if is_win and sys.version_info >= (3, 8):
    from asyncio import WindowsSelectorEventLoopPolicy

    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

logger = logging.getLogger()


def websockets():
    __start_wss_server(port=config.get('server_port'), logger=logger)


def proxy():
    __start_proxy(
        server_token=config.get('server_token'),
        server_host=config.get('server_host'),
        server_port=config.get('server_port'),
        proxy_port=config.get('proxy_port'),
        logger=logger
    )


def main():
    parser = argparse.ArgumentParser(
        description='Touchance Warp',
        usage='''<command> [<args>]
    The most commonly used git commands are:
       websockets     start a websocket server
       proxy          start a proxy client
    ''')
    parser.add_argument('command')
    try:
        args = parser.parse_args(sys.argv[1:2])
        if args.command is not None and args.command not in globals():
            print('Unrecognized command')
            parser.print_help()
        else:
            globals()[args.command]()
    except:
        pass


if __name__ == '__main__':
    main()
