import asyncio

from touchance.exceptions import SubscribeException
from touchance.quant_bridge import TCore


class QuoteAPI(TCore):
    port = '51237'

    async def subscribe_quote(self, quote_symbol: str):
        return await self.subscribe('SUBQUOTE', {'Symbol': quote_symbol, 'SubDataType': 'REALTIME'})

    async def unsubscribe_quote(self, quote_symbol: str):
        return await self.subscribe('UNSUBQUOTE', {'Symbol': quote_symbol, 'SubDataType': 'REALTIME'})

    async def subscribe_greeks(self, quote_symbol: str, greeks_type='REAL'):
        return await self.subscribe('SUBQUOTE', {
            'Symbol': quote_symbol, 'SubDataType': 'GREEKS', 'GreeksType': greeks_type
        })

    async def unsubscribe_greeks(self, quote_symbol: str, greeks_type='REAL'):
        return await self.subscribe('UNSUBQUOTE', {
            'Symbol': quote_symbol, 'SubDataType': 'GREEKS', 'GreeksType': greeks_type
        })

    async def subscribe_history(self, quote_symbol: str, data_type: str, start_time: str, end_time: str):
        """訂閱歷史資料.

        Parameters
        ----------
        quote_symbol: str
        data_type: str
            TICKS, 1K, DK
        start_time: str
        end_time: str
        """
        return await self.subscribe('SUBQUOTE', {
            'Symbol': quote_symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time
        })

    async def unsubscribe_history(self, quote_symbol: str, data_type: str, start_time: str, end_time: str):
        """取溑訂閱歷史資料.

        Parameters
        ----------
        quote_symbol: str
        data_type: str
            TICKS, 1K, DK
        start_time: str
        end_time: str
        """
        return await self.subscribe('UNSUBQUOTE', {
            'Symbol': quote_symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time
        })

    async def subscribe(self, request: str, param: dict):
        info = await self._send({'Request': request, 'SessionKey': self.session_key, 'Param': param})

        return info.get('Reply') == request and info.get('Success') == 'OK'

    async def get_history(self, quote_symbol: str, data_type: str, start_time: str, end_time: str, qry_index):
        return await self._send({'Request': 'GETHISDATA', 'SessionKey': self.session_key, 'Param': {
            'Symbol': quote_symbol, 'SubDataType': data_type, 'StartTime': start_time, 'EndTime': end_time,
            'QryIndex': qry_index
        }})

    async def get_histories(self, quote_symbol: str, data_type: str, start_time: str, end_time: str, retry=30):
        try:
            await self.subscribe_history(quote_symbol, data_type, start_time, end_time)
        except SubscribeException as e:
            self._logger.error(str(e))
        await self.pong()
        async for history in self.__get_histories(quote_symbol, data_type, start_time, end_time, retry):
            yield history

    async def __get_histories(self, quote_symbol: str, data_type: str, start_time: str, end_time: str, retry=30):
        info = {'Symbol': quote_symbol}
        qry_index = ''
        has_data = False
        while True:
            data = await self.get_history(quote_symbol, data_type, start_time, end_time, qry_index)

            histories = data.get('HisData', []) if data is not None else []

            if len(histories) == 0:
                retry -= 1
                if retry <= 0 or has_data is True:
                    break
                await asyncio.sleep(1)
                continue

            has_data = True
            for history in histories:
                yield {
                    'DataType': data_type,
                    'StartTime': start_time,
                    'EndTime': end_time,
                    'HisData': {**info, **history}
                }

            qry_index = histories[-1].get('QryIndex')
