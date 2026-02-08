"""
Deribit API Skill for Claude Agents

A comprehensive package for authenticating and trading on Deribit's
cryptocurrency derivatives exchange.

Usage:
    from deribit import DeribitAuth, DeribitTrader, DeribitLogger

    # Initialize logger (logs to ~/deribit/logs/)
    logger = DeribitLogger()

    # Authenticate
    auth = DeribitAuth(test_mode=True, logger=logger)
    auth.authenticate_credentials(scope="trade:read_write")

    # Trade (all operations are automatically logged)
    trader = DeribitTrader(auth)
    ticker = trader.get_ticker("BTC-PERPETUAL")
"""

from .deribit_auth import DeribitAuth
from .deribit_trader import DeribitTrader
from .deribit_logger import DeribitLogger

__version__ = "1.1.0"
__all__ = ["DeribitAuth", "DeribitTrader", "DeribitLogger"]
