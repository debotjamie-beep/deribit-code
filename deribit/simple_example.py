"""
Simple Example Script - Deribit Test API

This script demonstrates basic authentication and market data retrieval.
Safe to run - only reads data, doesn't place any orders.
"""

from deribit_auth import DeribitAuth
from deribit_trader import DeribitTrader


def main():
    print("=" * 70)
    print("Simple Deribit Test API Example")
    print("=" * 70)
    print()

    # Step 1: Authenticate
    print("Step 1: Authenticating...")
    print("-" * 70)
    try:
        auth = DeribitAuth(test_mode=True)
        auth.authenticate_credentials(scope="trade:read_write session:example")
        print("Authentication successful!\n")
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set your API credentials:")
        print("  export DERIBIT_CLIENT_ID='your_client_id'")
        print("  export DERIBIT_CLIENT_SECRET='your_client_secret'")
        return
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    # Step 2: Initialize trader
    trader = DeribitTrader(auth)

    # Step 3: Get account balance
    print("Step 2: Getting Account Balance...")
    print("-" * 70)
    try:
        summary = trader.get_account_summary(currency="BTC")
        balance = summary.get('balance', 0)
        equity = summary.get('equity', 0)
        print(f"Balance: {balance} BTC")
        print(f"Equity: {equity} BTC\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Step 4: Get current BTC price
    print("Step 3: Getting BTC-PERPETUAL Market Price...")
    print("-" * 70)
    try:
        ticker = trader.get_ticker("BTC-PERPETUAL")
        last_price = ticker.get('last_price')
        mark_price = ticker.get('mark_price')
        volume_24h = ticker.get('stats', {}).get('volume', 0)

        print(f"Last Price: ${last_price:,.2f}")
        print(f"Mark Price: ${mark_price:,.2f}")
        print(f"24h Volume: {volume_24h:,.2f} BTC\n")
    except Exception as e:
        print(f"Error: {e}\n")

    # Step 5: Get top 3 instruments
    print("Step 4: Getting Top 3 BTC Futures...")
    print("-" * 70)
    try:
        instruments = trader.get_instruments(currency="BTC", kind="future")
        for i, inst in enumerate(instruments[:3], 1):
            name = inst['instrument_name']
            print(f"{i}. {name}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")

    # Step 6: Check for open positions
    print("Step 5: Checking Open Positions...")
    print("-" * 70)
    try:
        positions = trader.get_positions(currency="BTC")
        if positions:
            print(f"You have {len(positions)} open position(s):")
            for pos in positions:
                print(f"  - {pos['instrument_name']}: {pos['size']} contracts")
        else:
            print("No open positions")
        print()
    except Exception as e:
        print(f"Error: {e}\n")

    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Check deribit_trader.py for more trading functions")
    print("  2. Read README.md for detailed documentation")
    print("  3. Visit https://docs.deribit.com/ for full API reference")


if __name__ == "__main__":
    main()
