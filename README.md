時間採用UTC+0

---

### Ping

#### 回應

```json
{
  "DataType": "PING"
}
```

---

### 全部合約查詢

#### 請求

```json
{
  "Request": "QUERYALLINSTRUMENT",
  "Type": "Fut"
}
```

> Type:Fut(期貨) or Opt(選擇權) or Fut2(個股期貨)

#### 回應

```json
{
  "Reply": "QUERYALLINSTRUMENT",
  "Success": "OK",
  "Instruments": {
    "CHT": "\u671f\u8ca8",
    "CHS": "\u671f\u8ca8",
    "ENG": "TOUCHANCE_FUT",
    "EXGID": "",
    "Node": [
      {
        "CHT": "\u53f0\u7063\u671f\u8ca8\u4ea4\u6613\u6240",
        "CHS": "\u53f0\u7063\u671f\u8ca8\u4ea4\u6613\u6240",
        "ENG": "TWF",
        "EXGID": "",
        "Node": [
          {
            "CHT": "\u71b1\u9580\u6708",
            "CHS": "\u70ed\u95e8\u6708",
            "ENG": "HOT",
            "Contracts": [
              "TC.F.TWF.FITX.202207",
              "TC.F.TWF.FIMTX.202207"
            ],
            "SYMBOL": "",
            "ExpirationDate": [
              "20220720",
              "20220720"
            ],
            "LongMarginRate": [
              null,
              null
            ],
            "ShortMarginRate": [
              null,
              null
            ],
            "InstrumentID": [
              null,
              null
            ]
          },
          {
            "CHT": "\u6b21\u71b1\u9580\u6708",
            "CHS": "\u6b21\u70ed\u95e8\u6708",
            "ENG": "HOT2",
            "Contracts": [
              "TC.F.TWF.FITX.202208",
              "TC.F.TWF.FIMTX.202208"
            ],
            "SYMBOL": "",
            "ExpirationDate": [
              "20220817",
              "20220817"
            ],
            "LongMarginRate": [
              null,
              null
            ],
            "ShortMarginRate": [
              null,
              null
            ],
            "InstrumentID": [
              null,
              null
            ]
          },
          {
            "CHT": "\u81fa\u6307",
            "CHS": "\u53f0\u6307",
            "ENG": "TAIEX Futures",
            "Contracts": [
              "TC.F.TWF.FITX",
              "TC.F.TWF.FITX.202207",
              "TC.F.TWF.FITX.202208",
              "TC.F.TWF.FITX.202209",
              "TC.F.TWF.FITX.202212",
              "TC.F.TWF.FITX.202303",
              "TC.F.TWF.FITX.202306"
            ],
            "SYMBOL": "FITX",
            "ExpirationDate": [
              null,
              "20220720",
              "20220817",
              "20220921",
              "20221221",
              "20230315",
              "20230621"
            ],
            "InstrumentID": [
              null,
              null,
              null,
              null,
              null,
              null,
              null
            ],
            "LongMarginRate": [
              null,
              null,
              null,
              null,
              null,
              null,
              null
            ],
            "ShortMarginRate": [
              null,
              null,
              null,
              null,
              null,
              null,
              null
            ]
          },
          {
            "CHT": "\u53f0\u6307\u9078\u6ce2\u52d5\u7387",
            "CHS": "\u53f0\u6307\u9078\u6ce2\u52d5\u7387",
            "ENG": "TAIWANVIX",
            "Contracts": [
              "TC.F.TWF.TAIWANVIX"
            ],
            "SYMBOL": "TAIWANVIX",
            "ExpirationDate": [
              null
            ],
            "InstrumentID": [
              null
            ],
            "LongMarginRate": [
              null
            ],
            "ShortMarginRate": [
              null
            ]
          }
        ]
      }
    ]
  }
}
```

---

### 商品交易設定查詢

#### 請求

```json
{
  "Request": "QUERYINSTRUMENTINFO",
  "Symbol": "TC.F.TWF.FITX.HOT"
}
```

#### 回應

```json
{
  "Reply": "QUERYINSTRUMENTINFO",
  "Success": "OK",
  "Info": {
    "TC.F.TWF": {
      "Duration": "ROD;IOC;FOK;",
      "EXG.SIM": "TWF",
      "EXG.TC3": "TWF",
      "EXGName.CHS": "\u53f0\u6e7e\u671f\u4ea4\u6240",
      "EXGName.CHT": "\u53f0\u7063\u671f\u4ea4\u6240",
      "OpenCloseTime": "00:45~05:45",
      "OrderType": "MARKET;LIMIT;MWP;",
      "OrderTypeMX": "MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;",
      "OrderTypeMX.TC": "MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;",
      "Position": "A;O;C;",
      "ResetTime": "23:30",
      "Symbol.SS2": "I.F.TWF",
      "TimeZone": "Asia/Shanghai"
    },
    "TC.F.TWF.FITX": {
      "Currency": "TWD",
      "Denominator": "1",
      "Denominator.ML": "1",
      "Denominator.yuanta": "1",
      "Duration": "ROD;IOC;FOK;",
      "EXG": "TWF",
      "EXG.Entrust": "TWF",
      "EXG.ITS": "TWF",
      "EXG.ITS_KGI": "TWF",
      "EXG.ITS_TW": "TWF",
      "EXG.ML": "TWF",
      "EXG.PATS": "TWF",
      "EXG.SIM": "TWF",
      "EXG.TC3": "TWF",
      "EXG.dcn": "TWF",
      "EXG.mdc": "TAIFEX",
      "EXG.mo": "TWF",
      "EXG.yuanta": "TAIFEX",
      "EXGName.CHS": "\u53f0\u6e7e\u671f\u4ea4\u6240",
      "EXGName.CHT": "\u53f0\u7063\u671f\u4ea4\u6240",
      "Group.CHS": "\u6307\u6570",
      "Group.CHT": "\u6307\u6578",
      "Group.ENG": "Equities",
      "I3_TickSize": "1",
      "Multiplier.CTP": "1",
      "Multiplier.GQ2": "1",
      "Multiplier.GTS": "1",
      "Multiplier.ML": "1",
      "Multiplier.yuanta": "1",
      "Name.CHS": "\u53f0\u6307",
      "Name.CHT": "\u81fa\u6307",
      "Name.ENG": "TAIEX Futures",
      "OpenCloseTime": "00:45~05:45;07:00~21:00",
      "OrderType": "MARKET;LIMIT;MWP;",
      "OrderTypeMX": "MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;",
      "OrderTypeMX.TC": "MARKET:IOC,FOK;LIMIT:ROD,IOC,FOK;MWP:IOC,FOK;",
      "Position": "A;O;C;",
      "ResetTime": "06:50",
      "SettlementTime": "05:30",
      "ShowDeno": "1",
      "ShowDeno.Entrust": "1",
      "ShowDeno.concords": "1",
      "ShowDeno.dcn": "1",
      "ShowDeno.kgi": "1",
      "ShowDeno.pfcf": "1",
      "ShowDeno.tw": "1",
      "ShowDeno.wlf": "1",
      "ShowMulti": "1",
      "ShowMulti.Entrust": "1",
      "ShowMulti.concords": "1",
      "ShowMulti.dcn": "1",
      "ShowMulti.kgi": "1",
      "ShowMulti.pfcf": "1",
      "ShowMulti.tw": "1",
      "ShowMulti.wlf": "1",
      "Symbol": "FITX",
      "Symbol.Entrust": "FITX",
      "Symbol.GQ2": "ICE.TWF.FITX",
      "Symbol.ITS": "FITX",
      "Symbol.ITS_KGI": "FITX",
      "Symbol.ITS_TW": "FITX",
      "Symbol.ML": "FITX",
      "Symbol.PATS": "FITX",
      "Symbol.SIM": "FITX",
      "Symbol.SS2": "I.F.TWF.FITX",
      "Symbol.TC3": "ICE.TWF.FITX",
      "Symbol.TCDATA": "ICE.TWF.FITX",
      "Symbol.dcn": "FITX",
      "Symbol.mdc": "TXF",
      "Symbol.mo": "TXF",
      "Symbol.yuanta": "TXF",
      "TickSize": "1",
      "TickSize.Underlying": "0.01",
      "TicksPerPoint": "1",
      "TimeZone": "Asia/Shanghai",
      "Underlying.OpenCloseTime": "01:00~05:30",
      "Weight": "200",
      "lotLimitDay": "10",
      "lotLimitNight": "5",
      "pinyin": "tz"
    }
  }
}
```

---

### 訂閱指令

#### 請求

```json
{
  "Request": "SUBQUOTE",
  "Param": {
    "Symbol": "TC.F.TWF.FITX.HOT",
    "SubDataType": "REALTIME"
  }
}
```

#### 回應

```json
{
  "DataType": "REALTIME",
  "Quote": {
    "Symbol": "TC.F.TWF.FITX.HOT",
    "Exchange": "TWF",
    "ExchangeName": "台灣期交所",
    "Security": "FITX",
    "SecurityName": "臺指",
    "SecurityType": "6",
    "TradeQuantity": "2",
    "FilledTime": "10513",
    "TradeDate": "20220627",
    "FlagOfBuySell": "1",
    "OpenTime": "84500",
    "CloseTime": "50000",
    "BidVolume": "9",
    "BidVolume1": "10",
    "BidVolume2": "21",
    "BidVolume3": "27",
    "BidVolume4": "20",
    "BidVolume5": "0",
    "BidVolume6": "0",
    "BidVolume7": "0",
    "BidVolume8": "0",
    "BidVolume9": "0",
    "AskVolume": "8",
    "AskVolume1": "17",
    "AskVolume2": "32",
    "AskVolume3": "54",
    "AskVolume4": "30",
    "AskVolume5": "0",
    "AskVolume6": "0",
    "AskVolume7": "0",
    "AskVolume8": "0",
    "AskVolume9": "0",
    "TotalBidCount": "9264",
    "TotalBidVolume": "16893",
    "TotalAskCount": "8582",
    "TotalAskVolume": "15640",
    "BidSize": "8141",
    "AskSize": "8551",
    "FirstDerivedBidVolume": "2",
    "FirstDerivedAskVolume": "1",
    "BuyCount": "9264",
    "SellCount": "8582",
    "EndDate": "20220720",
    "BestBidVolume": "9",
    "BestAskVolume": "8",
    "BeginDate": "20220421",
    "YTradeDate": "0",
    "ExpiryDate": "24",
    "TradingPrice": "15274",
    "Change": "221",
    "TradeVolume": "13555",
    "OpeningPrice": "15205",
    "HighPrice": "15275",
    "LowPrice": "15201",
    "ClosingPrice": "",
    "ReferencePrice": "15053",
    "UpperLimitPrice": "16558",
    "LowerLimitPrice": "13548",
    "YClosedPrice": "15209",
    "YTradeVolume": "54549",
    "Bid": "15273",
    "Bid1": "15272",
    "Bid2": "15271",
    "Bid3": "15270",
    "Bid4": "15269",
    "Bid5": "",
    "Bid6": "",
    "Bid7": "",
    "Bid8": "",
    "Bid9": "",
    "Ask": "15275",
    "Ask1": "15276",
    "Ask2": "15277",
    "Ask3": "15278",
    "Ask4": "15279",
    "Ask5": "",
    "Ask6": "",
    "Ask7": "",
    "Ask8": "",
    "Ask9": "",
    "PreciseTime": "10513195000",
    "FirstDerivedBid": "15269",
    "FirstDerivedAsk": "15276",
    "SettlementPrice": "",
    "BestBid": "15273",
    "BestAsk": "15275",
    "Deposit": "",
    "TickSize": "",
    "TradeStatus": "",
    "OpenInterest": "0"
  }
}
```

---

### 解除訂閱指令

```json
{
  "Request": "UNSUBQUOTE",
  "Param": {
    "Symbol": "TC.F.TWF.FITX.HOT",
    "SubDataType": "REALTIME"
  }
}
```

---

### 歷史資料取得

#### 請求

```json
{
  "Request": "GETHISDATA",
  "Param": {
    "Symbol": "TC.F.TWF.FITX.HOT",
    "SubDataType": "1K",
    "StartTime": "2021030100",
    "EndTime": "2021031700"
  }
}
```

> 註1:SubDataType使用TICKS or 1K or DK，且填寫StartTime、EndTime，回補歷史資料。

#### 回應

```json
{
  "DataType": "1K",
  "StartTime": "2021030100",
  "EndTime": "2021031700",
  "HisData": {
    "Symbol": "TC.F.TWF.FITX.HOT",
    "Date": "20210316",
    "Time": "210000",
    "UpTick": "29",
    "UpVolume": "39",
    "DownTick": "60",
    "DownVolume": "87",
    "UnchVolume": "32125",
    "Open": "16329",
    "High": "16330",
    "Low": "16321",
    "Close": "16325",
    "Volume": "126",
    "OI": "",
    "QryIndex": "12540"
  }
}
```