時間採用UTC+0

---

### 全部合約查詢

> Type:Fut(期貨) or Opt(選擇權) or Fut2(個股期貨)

```json
{
  "Request": "QUERYALLINSTRUMENT",
  "Type": "Fut"
}
```

---

### 商品交易設定查詢

```json
{
  "Request": "QUERYINSTRUMENTINFO",
  "Symbol": "TC.F.TWF.FITX.HOT"
}
```

---

### 訂閱指令

```json
{
  "Request": "SUBQUOTE",
  "Param": {
    "Symbol": "TC.F.TWF.FITX.HOT",
    "SubDataType": "REALTIME"
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
