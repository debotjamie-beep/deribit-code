# Deribit Trading Skill — Deployment Guide

## Prerequisites

- Python 3.7+
- `pip` package manager
- Git
- Access to Deribit API credentials stored at:
  - **Test**: `/Users/jamiedebot/.openclaw/secrets/deribit_test.json`
  - **Production**: `/Users/jamiedebot/.openclaw/secrets/deribit.json`

## Deployment Steps

### 1. Clean any previous installation

```bash
rm -rf deribit-code
```

### 2. Clone the repository

```bash
git clone https://github.com/debotjamie-beep/deribit-code.git
cd deribit-code
```

### 3. Install dependencies

```bash
pip install -r deribit/requirements.txt
```

### 4. Set up credentials

For **test environment** (test.deribit.com):

```bash
cp /Users/jamiedebot/.openclaw/secrets/deribit_test.json deribit/credentials.json
```

For **production** (www.deribit.com) — only when fully tested and ready:

```bash
cp /Users/jamiedebot/.openclaw/secrets/deribit.json deribit/credentials.json
```

Verify `deribit/credentials.json` has this format:

```json
{
  "client_id": "...",
  "client_secret": "...",
  "test_mode": true
}
```

If the `test_mode` field is missing, add it (`true` for test, `false` for production).
If the JSON keys are named differently (e.g. `clientId` instead of `client_id`), rename them to match.

**Never commit `credentials.json` to git** — it is already in `.gitignore`.

### 5. Verify authentication works

```bash
cd deribit && python test_with_credentials.py
```

Expected output:

```
Authenticated successfully
  Scope: trade:read_write session:test
Connection Test Successful!
All Tests Passed!
```

If authentication fails, check:
- Credentials file exists and has correct format
- API key has the required scopes enabled on Deribit
- Network connectivity to test.deribit.com

## Usage

### Basic usage with logging

```python
from deribit_auth import DeribitAuth
from deribit_trader import DeribitTrader
from deribit_logger import DeribitLogger

# Initialize logger — logs written to ~/deribit/logs/
logger = DeribitLogger()

# Authenticate (credentials loaded automatically from credentials.json)
# test_mode=True for test.deribit.com, False for www.deribit.com
auth = DeribitAuth(test_mode=True, logger=logger)
auth.authenticate_credentials(scope="trade:read_write")

# Initialize trader (inherits logger from auth)
trader = DeribitTrader(auth)
```

### Market data

```python
ticker = trader.get_ticker("BTC-PERPETUAL")
order_book = trader.get_order_book("BTC-PERPETUAL", depth=5)
instruments = trader.get_instruments(currency="BTC", kind="future")
```

### Trading

```python
# Buy
order = trader.buy("BTC-PERPETUAL", amount=10, order_type="market")
order = trader.buy("BTC-PERPETUAL", amount=10, order_type="limit", price=95000)

# Sell
order = trader.sell("BTC-PERPETUAL", amount=10, order_type="market")

# Cancel
trader.cancel_order(order["order"]["order_id"])
trader.cancel_all_orders(currency="BTC")
```

### Account and positions

```python
summary = trader.get_account_summary(currency="BTC")
positions = trader.get_positions(currency="BTC")
open_orders = trader.get_open_orders(currency="BTC")
trades = trader.get_user_trades(currency="BTC", count=10)
```

## Log Files

All logs are written to `~/deribit/logs/` in JSONL format (one JSON object per line):

| File | Content |
|------|---------|
| `trades_YYYYMMDD.jsonl` | buy, sell, cancel, edit, close_position |
| `auth_YYYYMMDD.jsonl` | authentication, token refresh, session events |
| `api_YYYYMMDD.jsonl` | account queries, market data, position checks |

### Inspecting logs

```bash
# Today's trades
cat ~/deribit/logs/trades_$(date -u +%Y%m%d).jsonl | python -m json.tool

# Today's auth events
cat ~/deribit/logs/auth_$(date -u +%Y%m%d).jsonl | python -m json.tool

# Today's API calls
cat ~/deribit/logs/api_$(date -u +%Y%m%d).jsonl | python -m json.tool
```

### Log entry example (trade)

```json
{
  "timestamp": "2026-02-08T14:30:15.123+00:00",
  "log_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "action": "buy",
  "status": "success",
  "latency_ms": 245.3,
  "request": {
    "instrument_name": "BTC-PERPETUAL",
    "amount": 10,
    "type": "limit",
    "price": 95000.0
  },
  "response": {
    "order_id": "ETH-12345678",
    "order_state": "open",
    "direction": "buy",
    "filled_amount": 0,
    "average_price": 0,
    "commission": 0,
    "raw_response": {}
  },
  "error": null,
  "context": {
    "environment": "test",
    "base_url": "https://test.deribit.com",
    "api_method": "private/buy"
  }
}
```

## Important Notes

- Use `test_mode=True` with test credentials until trading logic is fully validated
- The `test_mode` parameter in `DeribitAuth()` determines which Deribit server is used, regardless of what is in `credentials.json`
- Logging is optional — omit the `logger` parameter and everything works without logging
- Sensitive data is never logged: `client_secret` and `refresh_token` are excluded, `client_id` is masked
