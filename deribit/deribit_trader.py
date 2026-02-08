"""
Deribit Trading Functions Module

This module provides trading functions that use the DeribitAuth authentication.
Includes functions for:
- Getting market data
- Placing orders (buy/sell)
- Managing positions
- Getting account information

All operations are logged to structured JSONL files when a logger is provided.

Author: API Developer
Environment: Deribit Test (test.deribit.com)
"""

import time
import requests
from typing import Dict, Any, List, Optional
from deribit_auth import DeribitAuth

try:
    from deribit_logger import DeribitLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

# API methods that are trade actions (logged to trades_*.jsonl)
_TRADE_METHODS = {
    "private/buy",
    "private/sell",
    "private/cancel",
    "private/edit",
    "private/close_position",
    "private/cancel_all",
    "private/cancel_all_by_currency",
    "private/cancel_all_by_instrument",
}

# Mapping from API method to human-readable event name for API logs
_API_EVENT_NAMES = {
    "private/get_account_summary": "account_summary",
    "private/get_positions": "get_positions",
    "private/get_open_orders_by_currency": "get_open_orders",
    "private/get_open_orders_by_instrument": "get_open_orders",
    "private/get_subaccounts": "get_subaccounts",
    "private/get_user_trades_by_currency": "get_user_trades",
    "private/get_user_trades_by_instrument": "get_user_trades",
    "public/get_instruments": "get_instruments",
    "public/get_order_book": "get_order_book",
    "public/ticker": "get_ticker",
}

# Mapping from API method to trade action name
_TRADE_ACTION_NAMES = {
    "private/buy": "buy",
    "private/sell": "sell",
    "private/cancel": "cancel",
    "private/edit": "edit",
    "private/close_position": "close_position",
    "private/cancel_all": "cancel_all",
    "private/cancel_all_by_currency": "cancel_all",
    "private/cancel_all_by_instrument": "cancel_all",
}


class DeribitTrader:
    """
    Deribit Trading Interface

    Provides high-level trading functions using authenticated API access.
    All operations are logged when a DeribitLogger is available via auth.logger.
    """

    def __init__(self, auth: DeribitAuth):
        """
        Initialize trader with authentication

        Args:
            auth: Authenticated DeribitAuth instance
        """
        self.auth = auth
        self.base_url = auth.base_url
        self.logger = getattr(auth, "logger", None)
        self._environment = getattr(auth, "_environment", "test")

    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make authenticated API request with automatic logging.

        Trade actions (buy/sell/cancel/edit/close) are logged to trades_*.jsonl.
        All other API calls are logged to api_*.jsonl.

        Args:
            method: API method name (e.g., 'private/buy')
            params: Request parameters

        Returns:
            API response result
        """
        url = f"{self.base_url}/api/v2/{method}"
        headers = self.auth.get_headers() if method.startswith("private/") else {}
        is_trade = method in _TRADE_METHODS

        start_time = time.time()
        try:
            response = self.auth.session.get(
                url,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            latency_ms = (time.time() - start_time) * 1000

            result = response.json()

            if "result" in result:
                api_result = result["result"]

                # Log success
                if self.logger:
                    if is_trade:
                        self.logger.log_trade(
                            action=_TRADE_ACTION_NAMES.get(method, method),
                            request_params=params,
                            api_method=method,
                            response=api_result,
                            latency_ms=latency_ms,
                            environment=self._environment,
                            base_url=self.base_url,
                        )
                    else:
                        self.logger.log_api(
                            event=_API_EVENT_NAMES.get(method, method),
                            api_method=method,
                            request_params=params,
                            response=api_result,
                            latency_ms=latency_ms,
                            environment=self._environment,
                            base_url=self.base_url,
                        )

                return api_result

            elif "error" in result:
                api_error = result["error"]
                error = Exception(f"API Error: {api_error}")

                # Log API error
                if self.logger:
                    error_dict = DeribitLogger.format_error(
                        exception=error,
                        error_code=api_error.get("code") if isinstance(api_error, dict) else None,
                        error_message=api_error.get("message") if isinstance(api_error, dict) else str(api_error),
                        http_status=response.status_code,
                    )
                    if is_trade:
                        self.logger.log_trade(
                            action=_TRADE_ACTION_NAMES.get(method, method),
                            request_params=params,
                            api_method=method,
                            error=error_dict,
                            latency_ms=latency_ms,
                            environment=self._environment,
                            base_url=self.base_url,
                        )
                    else:
                        self.logger.log_api(
                            event="api_error",
                            api_method=method,
                            request_params=params,
                            error=error_dict,
                            latency_ms=latency_ms,
                            environment=self._environment,
                            base_url=self.base_url,
                        )

                raise error
            else:
                error = Exception(f"Unexpected response: {result}")
                if self.logger:
                    error_dict = DeribitLogger.format_error(
                        exception=error,
                        http_status=response.status_code,
                    )
                    if is_trade:
                        self.logger.log_trade(
                            action=_TRADE_ACTION_NAMES.get(method, method),
                            request_params=params,
                            api_method=method,
                            error=error_dict,
                            latency_ms=latency_ms,
                            environment=self._environment,
                            base_url=self.base_url,
                        )
                    else:
                        self.logger.log_api(
                            event="api_error",
                            api_method=method,
                            request_params=params,
                            error=error_dict,
                            latency_ms=latency_ms,
                            environment=self._environment,
                            base_url=self.base_url,
                        )
                raise error

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            # Log network/HTTP errors (only if not already logged above)
            if self.logger and not str(e).startswith(("API Error:", "Unexpected response:")):
                http_status = getattr(getattr(e, "response", None), "status_code", None)
                error_dict = DeribitLogger.format_error(
                    exception=e,
                    http_status=http_status,
                )
                if is_trade:
                    self.logger.log_trade(
                        action=_TRADE_ACTION_NAMES.get(method, method),
                        request_params=params,
                        api_method=method,
                        error=error_dict,
                        latency_ms=latency_ms,
                        environment=self._environment,
                        base_url=self.base_url,
                    )
                else:
                    self.logger.log_api(
                        event="api_error",
                        api_method=method,
                        request_params=params,
                        error=error_dict,
                        latency_ms=latency_ms,
                        environment=self._environment,
                        base_url=self.base_url,
                    )
            raise

    # =================================================================
    # ACCOUNT INFORMATION
    # =================================================================

    def get_account_summary(self, currency: str = "BTC", extended: bool = True) -> Dict[str, Any]:
        """
        Get account summary

        Args:
            currency: Currency (BTC, ETH, USDC, etc.)
            extended: Include additional fields

        Returns:
            Account summary with balance, equity, etc.
        """
        return self._make_request(
            "private/get_account_summary",
            {"currency": currency, "extended": extended}
        )

    def get_positions(self, currency: str = "BTC", kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current positions

        Args:
            currency: Currency (BTC, ETH, etc.)
            kind: Instrument kind (future, option, spot, etc.)

        Returns:
            List of open positions
        """
        params = {"currency": currency}
        if kind:
            params["kind"] = kind

        return self._make_request("private/get_positions", params)

    def get_subaccounts(self) -> List[Dict[str, Any]]:
        """
        Get list of subaccounts

        Returns:
            List of subaccounts
        """
        return self._make_request("private/get_subaccounts", {})

    # =================================================================
    # MARKET DATA
    # =================================================================

    def get_instruments(self, currency: str = "BTC", kind: Optional[str] = None,
                        expired: bool = False) -> List[Dict[str, Any]]:
        """
        Get available instruments

        Args:
            currency: Currency (BTC, ETH, etc.)
            kind: Instrument kind (future, option, spot)
            expired: Include expired instruments

        Returns:
            List of instruments
        """
        params = {"currency": currency, "expired": expired}
        if kind:
            params["kind"] = kind

        return self._make_request("public/get_instruments", params)

    def get_order_book(self, instrument_name: str, depth: int = 10) -> Dict[str, Any]:
        """
        Get order book for an instrument

        Args:
            instrument_name: Instrument name (e.g., 'BTC-PERPETUAL')
            depth: Order book depth

        Returns:
            Order book with bids and asks
        """
        return self._make_request(
            "public/get_order_book",
            {"instrument_name": instrument_name, "depth": depth}
        )

    def get_ticker(self, instrument_name: str) -> Dict[str, Any]:
        """
        Get ticker data for an instrument

        Args:
            instrument_name: Instrument name (e.g., 'BTC-PERPETUAL')

        Returns:
            Ticker data with current price, volume, etc.
        """
        return self._make_request(
            "public/ticker",
            {"instrument_name": instrument_name}
        )

    # =================================================================
    # TRADING - PLACING ORDERS
    # =================================================================

    def buy(
        self,
        instrument_name: str,
        amount: float,
        order_type: str = "market",
        price: Optional[float] = None,
        post_only: bool = False,
        reduce_only: bool = False,
        label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Place a buy order

        Args:
            instrument_name: Instrument name (e.g., 'BTC-PERPETUAL')
            amount: Order amount in contracts
            order_type: Order type ('market', 'limit', 'stop_limit', etc.)
            price: Limit price (required for limit orders)
            post_only: Post-only order (only maker)
            reduce_only: Reduce-only order (close position only)
            label: User-defined label

        Returns:
            Order details including order_id
        """
        params: Dict[str, Any] = {
            "instrument_name": instrument_name,
            "amount": amount,
            "type": order_type,
        }

        if price is not None:
            params["price"] = price
        if post_only:
            params["post_only"] = True
        if reduce_only:
            params["reduce_only"] = True
        if label:
            params["label"] = label

        return self._make_request("private/buy", params)

    def sell(
        self,
        instrument_name: str,
        amount: float,
        order_type: str = "market",
        price: Optional[float] = None,
        post_only: bool = False,
        reduce_only: bool = False,
        label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Place a sell order

        Args:
            instrument_name: Instrument name (e.g., 'BTC-PERPETUAL')
            amount: Order amount in contracts
            order_type: Order type ('market', 'limit', 'stop_limit', etc.)
            price: Limit price (required for limit orders)
            post_only: Post-only order (only maker)
            reduce_only: Reduce-only order (close position only)
            label: User-defined label

        Returns:
            Order details including order_id
        """
        params: Dict[str, Any] = {
            "instrument_name": instrument_name,
            "amount": amount,
            "type": order_type,
        }

        if price is not None:
            params["price"] = price
        if post_only:
            params["post_only"] = True
        if reduce_only:
            params["reduce_only"] = True
        if label:
            params["label"] = label

        return self._make_request("private/sell", params)

    # =================================================================
    # ORDER MANAGEMENT
    # =================================================================

    def get_open_orders(
        self,
        currency: Optional[str] = None,
        kind: Optional[str] = None,
        instrument_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get open orders

        Args:
            currency: Filter by currency (BTC, ETH, etc.)
            kind: Filter by kind (future, option)
            instrument_name: Filter by specific instrument

        Returns:
            List of open orders
        """
        if instrument_name:
            params: Dict[str, Any] = {"instrument_name": instrument_name}
            if kind:
                params["type"] = kind
            return self._make_request("private/get_open_orders_by_instrument", params)
        else:
            params = {"currency": currency or "BTC"}
            if kind:
                params["kind"] = kind
            return self._make_request("private/get_open_orders_by_currency", params)

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order

        Args:
            order_id: Order ID to cancel

        Returns:
            Cancelled order details
        """
        return self._make_request(
            "private/cancel",
            {"order_id": order_id}
        )

    def cancel_all_orders(self, currency: Optional[str] = None,
                          kind: Optional[str] = None,
                          instrument_name: Optional[str] = None) -> int:
        """
        Cancel all orders, optionally filtered by currency or instrument.

        Args:
            currency: Filter by currency
            kind: Filter by kind
            instrument_name: Filter by specific instrument

        Returns:
            Number of cancelled orders
        """
        if instrument_name:
            params: Dict[str, Any] = {"instrument_name": instrument_name}
            if kind:
                params["type"] = kind
            return self._make_request("private/cancel_all_by_instrument", params)
        elif currency:
            params = {"currency": currency}
            if kind:
                params["kind"] = kind
            return self._make_request("private/cancel_all_by_currency", params)
        else:
            return self._make_request("private/cancel_all", {})

    def edit_order(
        self,
        order_id: str,
        amount: float,
        price: float
    ) -> Dict[str, Any]:
        """
        Edit an existing order

        Args:
            order_id: Order ID to edit
            amount: New amount
            price: New price

        Returns:
            Updated order details
        """
        return self._make_request(
            "private/edit",
            {
                "order_id": order_id,
                "amount": amount,
                "price": price
            }
        )

    # =================================================================
    # POSITION MANAGEMENT
    # =================================================================

    def close_position(
        self,
        instrument_name: str,
        order_type: str = "market",
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Close a position

        Args:
            instrument_name: Instrument name
            order_type: Order type for closing ('market' or 'limit')
            price: Limit price (for limit orders)

        Returns:
            Order details
        """
        params: Dict[str, Any] = {
            "instrument_name": instrument_name,
            "type": order_type
        }
        if price is not None:
            params["price"] = price

        return self._make_request("private/close_position", params)

    # =================================================================
    # TRADE HISTORY
    # =================================================================

    def get_user_trades(
        self,
        currency: Optional[str] = None,
        instrument_name: Optional[str] = None,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get user trade history

        Args:
            currency: Filter by currency
            instrument_name: Filter by instrument
            count: Number of trades to return

        Returns:
            List of trades
        """
        if instrument_name:
            params: Dict[str, Any] = {
                "instrument_name": instrument_name,
                "count": count
            }
            return self._make_request("private/get_user_trades_by_instrument", params)
        else:
            params = {
                "currency": currency or "BTC",
                "count": count
            }
            return self._make_request("private/get_user_trades_by_currency", params)


def main():
    """
    Example usage of DeribitTrader
    """
    print("=" * 70)
    print("Deribit Trading Functions Demo")
    print("=" * 70)

    # Initialize logger
    logger = None
    if LOGGER_AVAILABLE:
        logger = DeribitLogger()
        print(f"Logging to: {logger.log_dir}")

    # Initialize authentication
    auth = DeribitAuth(test_mode=True, logger=logger)
    auth.authenticate_credentials(scope="trade:read_write session:trading_demo")

    # Initialize trader
    trader = DeribitTrader(auth)

    # =================================================================
    # EXAMPLE 1: Get Account Information
    # =================================================================
    print("\n[1] Account Summary")
    print("-" * 70)
    try:
        summary = trader.get_account_summary(currency="BTC")
        print(f"Currency: {summary.get('currency')}")
        print(f"Balance: {summary.get('balance')} BTC")
        print(f"Equity: {summary.get('equity')} BTC")
        print(f"Available Funds: {summary.get('available_funds')} BTC")
    except Exception as e:
        print(f"Error: {e}")

    # =================================================================
    # EXAMPLE 2: Get Market Data
    # =================================================================
    print("\n[2] Market Data - BTC-PERPETUAL")
    print("-" * 70)
    try:
        ticker = trader.get_ticker("BTC-PERPETUAL")
        print(f"Last Price: ${ticker.get('last_price')}")
        print(f"Mark Price: ${ticker.get('mark_price')}")
        print(f"24h Volume: {ticker.get('stats', {}).get('volume')} BTC")
        print(f"Bid: ${ticker.get('best_bid_price')}")
        print(f"Ask: ${ticker.get('best_ask_price')}")
    except Exception as e:
        print(f"Error: {e}")

    # =================================================================
    # EXAMPLE 3: Get Available Instruments
    # =================================================================
    print("\n[3] Available BTC Futures")
    print("-" * 70)
    try:
        instruments = trader.get_instruments(currency="BTC", kind="future")
        print(f"Found {len(instruments)} futures")
        for inst in instruments[:5]:  # Show first 5
            print(f"  - {inst['instrument_name']}")
    except Exception as e:
        print(f"Error: {e}")

    # =================================================================
    # EXAMPLE 4: Get Order Book
    # =================================================================
    print("\n[4] Order Book - BTC-PERPETUAL (Top 5)")
    print("-" * 70)
    try:
        book = trader.get_order_book("BTC-PERPETUAL", depth=5)
        print("Asks (Sell Orders):")
        for ask in book.get('asks', [])[:5]:
            print(f"  ${ask[0]} x {ask[1]} contracts")
        print("\nBids (Buy Orders):")
        for bid in book.get('bids', [])[:5]:
            print(f"  ${bid[0]} x {bid[1]} contracts")
    except Exception as e:
        print(f"Error: {e}")

    # =================================================================
    # EXAMPLE 5: Get Positions
    # =================================================================
    print("\n[5] Current Positions")
    print("-" * 70)
    try:
        positions = trader.get_positions(currency="BTC")
        if positions:
            for pos in positions:
                print(f"Instrument: {pos['instrument_name']}")
                print(f"  Size: {pos.get('size')} contracts")
                print(f"  Direction: {pos.get('direction')}")
                print(f"  Average Price: ${pos.get('average_price')}")
                print(f"  P&L: {pos.get('total_profit_loss')} BTC")
                print()
        else:
            print("No open positions")
    except Exception as e:
        print(f"Error: {e}")

    # =================================================================
    # EXAMPLE 6: Get Open Orders
    # =================================================================
    print("\n[6] Open Orders")
    print("-" * 70)
    try:
        orders = trader.get_open_orders(currency="BTC")
        if orders:
            for order in orders:
                print(f"Order ID: {order['order_id']}")
                print(f"  Instrument: {order['instrument_name']}")
                print(f"  Direction: {order['direction']}")
                print(f"  Amount: {order['amount']} contracts")
                print(f"  Price: ${order.get('price', 'Market')}")
                print(f"  Status: {order['order_state']}")
                print()
        else:
            print("No open orders")
    except Exception as e:
        print(f"Error: {e}")

    # =================================================================
    # EXAMPLE 7: PLACE ORDER (Commented out for safety)
    # =================================================================
    print("\n[7] Place Order Example (COMMENTED OUT)")
    print("-" * 70)
    print("# Uncomment to test placing orders:")
    print("#")
    print("# # Place a limit buy order")
    print("# order = trader.buy(")
    print("#     instrument_name='BTC-PERPETUAL',")
    print("#     amount=10,")
    print("#     order_type='limit',")
    print("#     price=50000,")
    print("#     post_only=True,")
    print("#     label='demo_order'")
    print("# )")
    print("# print(f\"Order placed: {order['order_id']}\")")
    print("#")
    print("# # Cancel the order")
    print("# trader.cancel_order(order['order_id'])")
    print("# print(\"Order cancelled\")")

    print("\n" + "=" * 70)
    print("Demo completed!")
    if logger:
        print(f"Logs written to: {logger.log_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
