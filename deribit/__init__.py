"""
Deribit API Skill for Claude Agents

A comprehensive package for authenticating and trading on Deribit's
cryptocurrency derivatives exchange.

Usage:
    from deribit import DeribitAuth, DeribitTrader
    
    # Authenticate
    auth = DeribitAuth(test_mode=True)
    auth.authenticate_credentials(scope="trade:read_write")
    
    # Trade
    trader = DeribitTrader(auth)
    ticker = trader.get_ticker("BTC-PERPETUAL")
"""

from .deribit_auth import DeribitAuth
from .deribit_trader import DeribitTrader

__version__ = "1.0.0"
__all__ = ["DeribitAuth", "DeribitTrader"]
