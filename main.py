import asyncio
import datetime

from touchance.quant_bridge import QuoteAPI


def OnRealTimeQuote(symbol):
    print(
        '交易所: %s, 訂閱目標: %s, 開: %s, 高: %s, 低: %s, 收: %s, 交易口數: %s, 交易量: %s, 買價: %s, 買量: %s, 賣價: %s, 賣量: %s' % (
            symbol['ExchangeName'],
            symbol['SecurityName'],
            symbol['OpeningPrice'],
            symbol['HighPrice'],
            symbol['LowPrice'],
            symbol['TradingPrice'],
            symbol['TradeQuantity'],
            symbol['TradeVolume'],
            symbol['Bid1'],
            symbol['BidVolume'],
            symbol['Ask1'],
            symbol['AskVolume']
        )
    )
    # print("商品：", symbol["Symbol"], "成交價:", symbol["TradingPrice"], "開:", symbol["OpeningPrice"], "高:",
    #       symbol["HighPrice"], "低:", symbol["LowPrice"])
    # print("整合資料Quote=", symbol)
    # print("交易所", symbol['ExchangeName'])
    # print("訂閱目標：", symbol['SecurityName'])
    # print("合約名稱：", symbol['Symbol'])
    # print("開：", symbol['OpeningPrice'])
    # print("高：", symbol['HighPrice'])
    # print("低：", symbol['LowPrice'])
    # print("收：", symbol['TradingPrice'])
    # print("交易口數：", symbol['TradeQuantity'])
    # print("交易量：", symbol['TradeVolume'])
    # print("買價：", symbol['Bid1'])
    # print("買量：", symbol['BidVolume'])
    # print("賣價：", symbol['Ask1'])
    # print("賣量：", symbol['AskVolume'])


async def history(quote_api):
    symbol = 'TC.F.TWF.FITX.HOT'
    data_type = '1K'
    start_time = '2021030100'
    end_time = '2021031700'

    quote_api.on('message', lambda data: print(data))
    quote_api.on('history', lambda data: print(data))

    # print(await quote_api.unsubscribe_history(symbol, data_type, start_time, end_time))
    # print(await quote_api.subscribe_history(symbol, data_type, start_time, end_time))
    async for his_data in quote_api.get_histories(symbol, data_type, start_time, end_time):
        print(his_data)


async def subscribe(quote_api):
    quote_api.on('REALTIME', lambda data: print(datetime.datetime.now()))
    quote_api.on('REALTIME', lambda data: OnRealTimeQuote(data['Quote']))
    # quote_api.on('GREEKS', lambda data: print('GREEKS', data))

    # print(await quote_api.query_instrument_info('TC.F.TWF.FITX.HOT'))
    await quote_api.unsubscribe_quote('TC.F.TWF.FITX.HOT')
    await quote_api.subscribe_quote('TC.F.TWF.FITX.HOT')
    await quote_api.unsubscribe_quote('TC.F.CBOT.YM.202209')
    await quote_api.subscribe_quote('TC.F.CBOT.YM.202209')
    # await quote_api.unsubscribe_greeks('TC.F.CBOT.YM.202209')
    # await quote_api.subscribe_greeks('TC.F.CBOT.YM.202209')


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()

    quote_api = QuoteAPI(event_loop=loop)
    await quote_api.connect()
    quote_api.serve()

    print(quote_api.sub_port)

    quote_api.on('PING', lambda data: print(datetime.datetime.now()))
    quote_api.on('PING', lambda data: print(data))

    # quote_api.query_all_instrument('Fut')
    await asyncio.gather(
        # subscribe(quote_api),
        history(quote_api)
    )

    await stop


if __name__ == '__main__':
    asyncio.run(main())
