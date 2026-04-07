# MarketData.app Options API Skill

美股/港股/期权实时行情查询，基于 MarketData.app API。

## API 基础信息

- **无需 API Key**（免费额度每天 100 次请求，注册获取更多）
- **注册地址：** https://marketdata.app/signup/
- **Base URL:** `https://api.marketdata.app/v1`
- **文档：** https://www.marketdata.app/docs/api/options

## 支持的查询类型

### 1. 期权链（Option Chain）
```
GET /options/chain/{symbol}/
```
查询某标的的所有期权合约列表（支持股票期权、ETF期权、指数期权）。

**示例：**
```bash
curl -s "https://api.marketdata.app/v1/options/chain/AAPL/?dateformat=timestamp"
```

**返回字段：**
- `optionSymbol` - 期权合约代码（如 AAPL260417C00200000）
- `expiration` - 到期日
- `strike` - 行权价
- `side` - C(Call)/P(Put)

---

### 2. 期权实时报价
```
GET /options/quotes/{optionSymbol}/
```
查询单个期权合约的实时价格和 Greeks。

**示例：**
```bash
curl -s "https://api.marketdata.app/v1/options/quotes/AAPL260417C00200000/?dateformat=timestamp"
```

**返回字段：**
| 字段 | 说明 |
|------|------|
| `bid` / `ask` | 买价 / 卖价 |
| `bidSize` / `askSize` | 买卖盘口量 |
| `mid` | 中价 |
| `last` | 最新成交价 |
| `volume` | 成交量 |
| `openInterest` | 持仓量 |
| `inTheMoney` | 是否价内 |
| `intrinsicValue` | 内在价值 |
| `extrinsicValue` | 外在价值 |
| `iv` | 隐含波动率 |
| `delta` / `gamma` / `theta` / `vega` | Greeks |

---

### 3. 批量查询（一次获取整条链的报价）
对 `options/chain` 返回的多个合约，可以分批调用 `/options/quotes/` 查询报价。

**注意：** 免费额度每天 100 次，注意不要超限。

---

### 4. 历史数据
```
GET /options/history/{optionSymbol}/?from=YYYY-MM-DD&to=YYYY-MM-DD
```
获取期权历史价格。

---

## 代码示例

### Shell（curl）
```bash
# 获取期权链
curl -s "https://api.marketdata.app/v1/options/chain/AAPL/?dateformat=timestamp"

# 获取单个期权报价
curl -s "https://api.marketdata.app/v1/options/quotes/AAPL260417C00200000/?dateformat=timestamp"
```

### Python
```python
import requests

# 获取期权链
def get_option_chain(symbol):
    url = f"https://api.marketdata.app/v1/options/chain/{symbol}/"
    r = requests.get(url, params={"dateformat": "timestamp"})
    return r.json()

# 获取期权报价
def get_option_quote(symbol):
    url = f"https://api.marketdata.app/v1/options/quotes/{symbol}/"
    r = requests.get(url, params={"dateformat": "timestamp"})
    return r.json()
```

## 使用场景

- 查询期权链（所有到期日 + 行权价）
- 获取实时 Greeks（Delta对冲、风控）
- IV 分析（期权定价/波动率交易）
- 批量导出期权数据做回测

## 注意事项

- 数据有 15 分钟延迟（免费版）
- 注册后每天 100 次请求额度
- 美股交易日 9:30-16:00（ET）数据最活跃
