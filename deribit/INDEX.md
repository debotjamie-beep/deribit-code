# Deribit Trading Skill Package

**Version:** 1.0.0  
**Environment:** Deribit Test & Production  
**For:** Claude AI Agents  

## 📦 Package Contents

```
deribit/
├── __init__.py                    # Package initialization
├── deribit_auth.py               # Authentication module ⭐
├── deribit_trader.py             # Trading functions module ⭐
├── simple_example.py             # Quick start example
├── test_with_credentials.py      # Full test script
├── authentication_demo.py        # Authentication walkthrough
├── SKILL.md                      # Skill documentation for agents
├── README.md                     # User documentation
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── GITHUB_UPLOAD_GUIDE.md       # How to upload to GitHub
├── upload_to_github.sh          # Automated upload script
└── INDEX.md                      # This file
```

## 🚀 Quick Start

### For Users

```bash
# 1. Install dependencies
pip install requests

# 2. Set your credentials
export DERIBIT_CLIENT_ID="your_client_id"
export DERIBIT_CLIENT_SECRET="your_client_secret"

# 3. Run example
python simple_example.py
```

### For Claude Agents

```python
from deribit import DeribitAuth, DeribitTrader

# Authenticate
auth = DeribitAuth(test_mode=True)
auth.authenticate_credentials(scope="trade:read_write")

# Trade
trader = DeribitTrader(auth)
ticker = trader.get_ticker("BTC-PERPETUAL")
```

## 📚 Documentation

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** | Complete user guide | Traders, Developers |
| **SKILL.md** | Agent integration guide | Claude Agents |
| **GITHUB_UPLOAD_GUIDE.md** | GitHub setup | Repository owners |

## 🔑 Core Modules

### 1. `deribit_auth.py` - Authentication

**Key Functions:**
- `authenticate_credentials()` - Simple auth with Client ID/Secret
- `authenticate_signature()` - Secure HMAC-SHA256 auth
- `refresh_access_token()` - Token renewal
- `get_headers()` - HTTP headers for API calls
- `is_token_valid()` - Check token expiry

**Features:**
- ✅ Multiple authentication methods
- ✅ Automatic token refresh
- ✅ Session management
- ✅ Test & production environments

### 2. `deribit_trader.py` - Trading Operations

**Account Management:**
- `get_account_summary()` - Balance, equity, margin
- `get_positions()` - Open positions
- `get_subaccounts()` - List subaccounts

**Market Data:**
- `get_instruments()` - Available instruments
- `get_order_book()` - Order book data
- `get_ticker()` - Current prices

**Trading:**
- `buy()` - Place buy order
- `sell()` - Place sell order

**Order Management:**
- `get_open_orders()` - List open orders
- `cancel_order()` - Cancel specific order
- `cancel_all_orders()` - Cancel all orders
- `edit_order()` - Modify existing order

**Position Management:**
- `close_position()` - Close position
- `get_user_trades()` - Trade history

## 🎯 Use Cases

### 1. Market Making Bot
```python
# Get order book
book = trader.get_order_book("BTC-PERPETUAL")

# Calculate mid-price
mid = (book['best_bid'] + book['best_ask']) / 2

# Place orders around mid
trader.buy(..., price=mid - 10)
trader.sell(..., price=mid + 10)
```

### 2. Portfolio Rebalancing
```python
# Check all positions
positions = trader.get_positions(currency="BTC")

# Close positions exceeding risk limits
for pos in positions:
    if abs(pos['size']) > MAX_SIZE:
        trader.close_position(pos['instrument_name'])
```

### 3. Automated Trading
```python
# Monitor market
ticker = trader.get_ticker("BTC-PERPETUAL")

# Execute strategy
if should_buy(ticker):
    trader.buy("BTC-PERPETUAL", amount=10, order_type="market")
```

## 🔐 Security

✅ Environment variables for credentials  
✅ HMAC-SHA256 signature authentication  
✅ Automatic token refresh  
✅ `.gitignore` configured to exclude secrets  
⚠️ Never commit credentials to Git  

## 📤 Upload to GitHub

### Quick Method (Web Interface)

1. Go to https://github.com/new
2. Create repository
3. Upload the entire `deribit` folder
4. Done!

### Command Line Method

```bash
cd deribit
./upload_to_github.sh
```

Or manually:
```bash
git init
git add .
git commit -m "Add Deribit skill"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

See **GITHUB_UPLOAD_GUIDE.md** for detailed instructions.

## 🧪 Testing

### Test Files Included

1. **simple_example.py** - Safe market data retrieval (no trading)
2. **test_with_credentials.py** - Full authentication test
3. **authentication_demo.py** - Shows auth process details

### Run Tests

```bash
# Demo (no API calls)
python authentication_demo.py

# Simple example (read-only)
python simple_example.py

# Full test (requires valid credentials)
python test_with_credentials.py
```

## 📋 Requirements

- **Python:** 3.7+
- **Dependencies:** `requests` (see requirements.txt)
- **API Access:** Deribit account with API key
- **Network:** Internet connection

## 🌐 Resources

- **Deribit API Docs:** https://docs.deribit.com/
- **Test Environment:** https://test.deribit.com
- **API Reference:** https://docs.deribit.com/api-reference
- **Support:** https://support.deribit.com/

## 📝 License

This skill package is provided as-is for educational and development purposes.

## 🤝 Contributing

To contribute or report issues:
1. Fork the repository
2. Make your changes
3. Submit a pull request

## 📧 Support

For questions about:
- **This skill package:** Open an issue on GitHub
- **Deribit API:** Contact Deribit support
- **Claude agents:** Refer to Anthropic documentation

## 🔄 Version History

- **1.0.0** (2025-02-06)
  - Initial release
  - Authentication module
  - Trading functions
  - Examples and documentation

## 🎓 Learning Path

1. Start with **authentication_demo.py** to understand auth
2. Run **simple_example.py** to see market data retrieval
3. Read **SKILL.md** for agent integration patterns
4. Study **deribit_trader.py** for available functions
5. Implement your trading strategy

## ⚡ Quick Reference

```python
# Import
from deribit import DeribitAuth, DeribitTrader

# Auth
auth = DeribitAuth(test_mode=True)
auth.authenticate_credentials()

# Trade
trader = DeribitTrader(auth)

# Common operations
ticker = trader.get_ticker("BTC-PERPETUAL")
positions = trader.get_positions("BTC")
order = trader.buy("BTC-PERPETUAL", 10, "limit", 50000)
trader.cancel_order(order['order_id'])
```

---

**Ready to upload to GitHub?** See `GITHUB_UPLOAD_GUIDE.md` 📤

**Ready to use with Claude agent?** See `SKILL.md` 🤖

**Ready to start trading?** See `simple_example.py` 📈
