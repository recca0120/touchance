import datetime

from src.touchance import QuoteAPI


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


def history(quote_api):
    symbol = 'TC.F.TWF.FITX.HOT'
    data_type = '1K'
    start_time = '2021030100'
    end_time = '2021031700'

    # quote_api.on('history', lambda data, info: print(data, info))

    print(quote_api.unsubscribe_history(symbol, data_type, start_time, end_time))
    print(quote_api.subscribe_history(symbol, data_type, start_time, end_time))


def subscribe(quote_api):
    quote_api.on('REALTIME', lambda data: print(datetime.datetime.now()))
    quote_api.on('REALTIME', lambda data: OnRealTimeQuote(data['Quote']))
    quote_api.on('PING', lambda data: print(datetime.datetime.now()))
    quote_api.on('PING', lambda data: print(data))
    quote_api.on('GREEKS', lambda data: print(data))

    # print(quote_api.query_instrument_info('TC.F.TWF.FITX.HOT'))
    quote_api.unsubscribe_quote('TC.F.TWF.FITX.HOT')
    quote_api.subscribe_quote('TC.F.TWF.FITX.HOT')
    quote_api.unsubscribe_quote('TC.F.CBOT.YM.202209')
    quote_api.subscribe_quote('TC.F.CBOT.YM.202209')
    quote_api.unsubscribe_greeks('TC.F.CBOT.YM.202209')
    quote_api.subscribe_greeks('TC.F.CBOT.YM.202209')


def main():
    quote_api = QuoteAPI()
    quote_api.connect()

    print(quote_api.sub_port)

    # quote_api.query_all_instrument('Fut')
    # subscribe(quote_api)
    history(quote_api)


if __name__ == '__main__':
    main()
