from typing import Union


class SessionIllegalException(Exception):
    pass


class SubscribeException(Exception):
    pass


class NewOrderException(Exception):
    def __init__(self, code: Union[str, int]):
        error_messages = {
            '-10': 'Unknown Error',
            '-11': '買賣別不對',
            '-13': '下單帳號, 不可下此交易所商品',
            '-14': '下單錯誤, 不支援的價格 或 OrderType 或 TimeInForce',
            '-15': '不支援證券下單',
            '-20': '連線未建立',
            '-22': '價格的TickSize錯誤',
            '-23': '下單數量超過該商品的上下限',
            '-24': '下單數量錯誤',
            '-25': '價格不能小於和等於0 (市價類型不會去檢查)',
        }
        self.code = str(code)
        self.message = error_messages[str(code)]
        super().__init__(self.message)
