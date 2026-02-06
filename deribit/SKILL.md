# Deribit Trading Skill

A comprehensive skill for Claude agents to authenticate and trade on Deribit's cryptocurrency derivatives exchange.

## Skill Overview

This skill enables Claude agents to:
- Authenticate with Deribit API (test and production)
- Retrieve market data and account information
- Place and manage orders
- Monitor positions and execute trades
- Handle token refresh and session management

## Prerequisites

- Python 3.7+
- Deribit API credentials (Client ID and Secret)
- `requests` library

## Installation

```bash
pip install requests
```

## Environment Variables

Set these environment variables with your Deribit API credentials:

```bash
export DERIBIT_CLIENT_ID="your_client_id"
export DERIBIT_CLIENT_SECRET="your_client_secret"
```

## Core Modules

### 1. Authentication (`deribit_auth.py`)

Handles all authentication methods:

```python
from deribit_auth import DeribitAuth

# Initialize with credentials
auth = DeribitAuth(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    test_mode=True  # Use False for production
)

# Authenticate (choose one method)
auth.authenticate_credentials(scope="trade:read_write")
auth.authenticate_signature(scope="trade:read_write")  # More secure

# Get headers for API requests
headers = auth.get_headers()
```

### 2. Trading (`deribit_trader.py`)

Provides high-level trading functions:

```python
from deribit_trader import DeribitTrader

# Initialize trader
trader = DeribitTrader(auth)

# Get account info
summary = trader.get_account_summary(currency="BTC")
positions = trader.get_positions(currency="BTC")

# Get market data
ticker = trader.get_ticker("BTC-PERPETUAL")
orderbook = trader.get_order_book("BTC-PERPETUAL")
instruments = trader.get_instruments(currency="BTC", kind="future")

# Place orders
buy_order = trader.buy(
    instrument_name="BTC-PERPETUAL",
    amount=10,
    order_type="limit",
    price=50000
)

sell_order = trader.sell(
    instrument_name="BTC-PERPETUAL",
    amount=10,
    order_type="market"
)

# Manage orders
orders = trader.get_open_orders(currency="BTC")
trader.cancel_order(order_id="123456")
trader.cancel_all_orders(currency="BTC")

# Close positions
trader.close_position(instrument_name="BTC-PERPETUAL")
```

## Agent Usage Patterns

### Pattern 1: Market Analysis

```python
# Agent analyzes market before trading
auth = DeribitAuth(test_mode=True)
auth.authenticate_credentials()
trader = DeribitTrader(auth)

# Get current market state
ticker = trader.get_ticker("BTC-PERPETUAL")
orderbook = trader.get_order_book("BTC-PERPETUAL", depth=20)

# Analyze spread
best_bid = orderbook['bids'][0][0]
best_ask = orderbook['asks'][0][0]
spread = best_ask - best_bid

print(f"Current spread: ${spread}")
```

### Pattern 2: Risk Management

```python
# Check positions and account balance before trading
summary = trader.get_account_summary(currency="BTC")
available_funds = summary['available_funds']

positions = trader.get_positions(currency="BTC")
total_exposure = sum(abs(p['size']) for p in positions)

print(f"Available: {available_funds} BTC")
print(f"Exposure: {total_exposure} contracts")
```

### Pattern 3: Order Execution

```python
# Place a smart limit order
ticker = trader.get_ticker("BTC-PERPETUAL")
current_price = ticker['last_price']

# Place order slightly above/below market
buy_price = current_price * 0.999  # 0.1% below market

order = trader.buy(
    instrument_name="BTC-PERPETUAL",
    amount=10,
    order_type="limit",
    price=buy_price,
    post_only=True,  # Only maker orders
    label="agent_trade_001"
)

print(f"Order placed: {order['order_id']}")
```

### Pattern 4: Position Monitoring

```python
# Monitor positions and close if needed
positions = trader.get_positions(currency="BTC")

for pos in positions:
    pnl = pos['total_profit_loss']
    
    # Close position if profit target hit
    if pnl > 0.01:  # 0.01 BTC profit
        trader.close_position(
            instrument_name=pos['instrument_name'],
            order_type="market"
        )
        print(f"Closed {pos['instrument_name']} with {pnl} BTC profit")
```

## Available Functions

### Account Management
- `get_account_summary(currency)` - Get balance, equity, margin
- `get_positions(currency, kind)` - Get open positions
- `get_subaccounts()` - List subaccounts

### Market Data
- `get_instruments(currency, kind)` - List available instruments
- `get_order_book(instrument_name, depth)` - Get order book
- `get_ticker(instrument_name)` - Get ticker data

### Trading
- `buy(instrument_name, amount, order_type, price, ...)` - Place buy order
- `sell(instrument_name, amount, order_type, price, ...)` - Place sell order

### Order Management
- `get_open_orders(currency, kind, instrument_name)` - Get open orders
- `cancel_order(order_id)` - Cancel specific order
- `cancel_all_orders(currency, kind, instrument_name)` - Cancel all orders
- `edit_order(order_id, amount, price)` - Edit existing order

### Position Management
- `close_position(instrument_name, order_type, price)` - Close position
- `get_user_trades(currency, instrument_name, count)` - Get trade history

## Authentication Scopes

Available scopes for API access:

- `account:read` - Read account information
- `account:read_write` - Full account management
- `trade:read` - Read trading data
- `trade:read_write` - Place and manage orders
- `wallet:read` - Read wallet information
- `wallet:read_write` - Withdraw and manage wallet
- `session:name` - Create persistent session

Example with multiple scopes:
```python
auth.authenticate_credentials(
    scope="trade:read_write wallet:read session:agent_001"
)
```

## Error Handling

```python
try:
    order = trader.buy(
        instrument_name="BTC-PERPETUAL",
        amount=10,
        order_type="limit",
        price=50000
    )
except Exception as e:
    print(f"Order failed: {e}")
    # Handle error appropriately
```

## Security Best Practices

1. **Use Environment Variables** for credentials
2. **Use Signature Authentication** for production
3. **Implement Rate Limiting** in agent logic
4. **Validate Inputs** before placing orders
5. **Monitor Token Expiry** and refresh automatically
6. **Test on Test Environment** before production

## Testing

Run the included examples:

```bash
# Demo authentication process
python authentication_demo.py

# Simple market data example
python simple_example.py

# Full test with your credentials
python test_with_credentials.py
```

## Limits and Constraints

- Max 16 sessions per API key
- Max 32 connections per IP
- Token lifetime: varies (typically 1 year for test)
- Rate limits apply to API calls

## Support

- Deribit Documentation: https://docs.deribit.com/
- API Reference: https://docs.deribit.com/api-reference
- Test Environment: https://test.deribit.com

## License

This skill is provided as-is for educational and development purposes.
