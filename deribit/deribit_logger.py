"""
Deribit Logger Module

Provides structured JSON logging for three categories:
- Trade logs:  ~/deribit/logs/trades_YYYYMMDD.jsonl
- Auth logs:   ~/deribit/logs/auth_YYYYMMDD.jsonl
- API logs:    ~/deribit/logs/api_YYYYMMDD.jsonl

Each log entry is a single JSON line (JSONL format) for easy
parsing by both humans and the future AuditAgent.

Sensitive data policy:
- client_secret: NEVER logged
- refresh_token: NEVER logged
- client_id: masked (first 4 chars + ****)
- access_token: only first 10 chars for correlation
"""

import json
import os
import time
import uuid
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class DeribitLogger:
    """
    Structured logger for Deribit trading operations.

    Writes JSONL files to ~/deribit/logs/ with three separate streams:
    - trades_YYYYMMDD.jsonl  (buy, sell, cancel, edit, close_position)
    - auth_YYYYMMDD.jsonl    (authentication, token refresh, session events)
    - api_YYYYMMDD.jsonl     (account queries, market data, position checks)
    """

    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize the logger.

        Args:
            log_dir: Custom log directory. Defaults to ~/deribit/logs/
        """
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = Path.home() / "deribit" / "logs"

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _today_stamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d")

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def _new_log_id(self) -> str:
        return str(uuid.uuid4())

    def _write_entry(self, category: str, entry: Dict[str, Any]) -> None:
        """
        Write a single JSONL entry to the appropriate log file.

        Args:
            category: Log category ('trades', 'auth', 'api')
            entry: The log entry dict
        """
        filename = f"{category}_{self._today_stamp()}.jsonl"
        filepath = self.log_dir / filename

        line = json.dumps(entry, default=str, ensure_ascii=False)

        with self._lock:
            with open(filepath, "a") as f:
                f.write(line + "\n")

    @staticmethod
    def mask_client_id(client_id: Optional[str]) -> Optional[str]:
        if not client_id:
            return None
        if len(client_id) <= 4:
            return "****"
        return client_id[:4] + "****"

    @staticmethod
    def mask_token(token: Optional[str]) -> Optional[str]:
        if not token:
            return None
        return token[:10] + "..."

    # =================================================================
    # TRADE LOGGING
    # =================================================================

    def log_trade(
        self,
        action: str,
        request_params: Dict[str, Any],
        api_method: str,
        response: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0,
        environment: str = "test",
        base_url: str = "",
    ) -> str:
        """
        Log a trade event (buy, sell, cancel, edit, close_position).

        Args:
            action: Trade action ('buy', 'sell', 'cancel', 'edit', 'close_position')
            request_params: Parameters sent to the API
            api_method: API endpoint called
            response: Parsed API response (on success)
            error: Error details dict (on failure)
            latency_ms: Round-trip time in milliseconds
            environment: 'test' or 'production'
            base_url: Deribit base URL used

        Returns:
            The log_id for this entry
        """
        log_id = self._new_log_id()
        status = "error" if error else "success"

        # Extract key response fields if available
        response_summary = None
        if response:
            # Trade responses nest order info under 'order'
            order = response.get("order", response)
            response_summary = {
                "order_id": order.get("order_id"),
                "order_state": order.get("order_state"),
                "direction": order.get("direction"),
                "filled_amount": order.get("filled_amount"),
                "average_price": order.get("average_price"),
                "commission": order.get("commission"),
                "raw_response": response,
            }

        entry = {
            "timestamp": self._now_iso(),
            "log_id": log_id,
            "action": action,
            "status": status,
            "latency_ms": round(latency_ms, 1),
            "request": request_params,
            "response": response_summary,
            "error": error,
            "context": {
                "environment": environment,
                "base_url": base_url,
                "api_method": api_method,
            },
        }

        self._write_entry("trades", entry)
        return log_id

    # =================================================================
    # AUTH LOGGING
    # =================================================================

    def log_auth(
        self,
        event: str,
        client_id: Optional[str] = None,
        method: Optional[str] = None,
        scope_requested: Optional[str] = None,
        scope_granted: Optional[str] = None,
        token_expires_in: Optional[int] = None,
        access_token: Optional[str] = None,
        credentials_source: Optional[str] = None,
        status: str = "success",
        latency_ms: float = 0,
        error: Optional[Dict[str, Any]] = None,
        environment: str = "test",
        base_url: str = "",
        api_method: Optional[str] = None,
    ) -> str:
        """
        Log an authentication/session event.

        Args:
            event: Event type ('auth_credentials', 'auth_signature',
                   'token_refresh', 'token_expired', 'auth_failure',
                   'session_start', 'session_end')
            client_id: Client ID (will be masked)
            method: Auth method used
            scope_requested: Scope requested
            scope_granted: Scope actually granted
            token_expires_in: Token TTL in seconds
            access_token: Access token (will be masked to prefix only)
            credentials_source: How credentials were loaded
            status: 'success' or 'error'
            latency_ms: Round-trip time
            error: Error details dict
            environment: 'test' or 'production'
            base_url: Deribit base URL
            api_method: API endpoint called

        Returns:
            The log_id for this entry
        """
        log_id = self._new_log_id()

        entry = {
            "timestamp": self._now_iso(),
            "log_id": log_id,
            "event": event,
            "status": status,
            "latency_ms": round(latency_ms, 1),
            "auth": {
                "method": method,
                "client_id": self.mask_client_id(client_id),
                "scope_requested": scope_requested,
                "scope_granted": scope_granted,
                "token_expires_in": token_expires_in,
                "token_prefix": self.mask_token(access_token),
            },
            "error": error,
            "context": {
                "environment": environment,
                "base_url": base_url,
                "api_method": api_method,
                "credentials_source": credentials_source,
            },
        }

        self._write_entry("auth", entry)
        return log_id

    # =================================================================
    # API LOGGING
    # =================================================================

    def log_api(
        self,
        event: str,
        api_method: str,
        request_params: Dict[str, Any],
        response: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0,
        environment: str = "test",
        base_url: str = "",
    ) -> str:
        """
        Log a non-trade API call (account, market data, positions, etc.).

        Args:
            event: Event type ('account_summary', 'get_positions',
                   'get_open_orders', 'get_instruments', 'get_ticker',
                   'get_order_book', 'get_user_trades', 'get_subaccounts',
                   'api_error', 'rate_limit')
            api_method: API endpoint called
            request_params: Parameters sent
            response: Parsed API response
            error: Error details dict
            latency_ms: Round-trip time
            environment: 'test' or 'production'
            base_url: Deribit base URL

        Returns:
            The log_id for this entry
        """
        log_id = self._new_log_id()
        status = "error" if error else "success"

        response_summary = None
        if response:
            # For list responses, include count
            if isinstance(response, list):
                response_summary = {
                    "result_count": len(response),
                    "raw_response": response,
                }
            else:
                response_summary = {
                    "result_count": 1,
                    "raw_response": response,
                }

        entry = {
            "timestamp": self._now_iso(),
            "log_id": log_id,
            "event": event,
            "status": status,
            "latency_ms": round(latency_ms, 1),
            "request": {
                "api_method": api_method,
                "params": request_params,
            },
            "response": response_summary,
            "error": error,
            "context": {
                "environment": environment,
                "base_url": base_url,
            },
        }

        self._write_entry("api", entry)
        return log_id

    # =================================================================
    # ERROR HELPERS
    # =================================================================

    @staticmethod
    def format_error(
        exception: Optional[Exception] = None,
        error_code: Optional[int] = None,
        error_message: Optional[str] = None,
        http_status: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build a standardized error dict for log entries.

        Args:
            exception: The Python exception caught
            error_code: Deribit API error code
            error_message: Deribit API error message
            http_status: HTTP status code

        Returns:
            Structured error dict
        """
        error_dict = {
            "error_code": error_code,
            "error_message": error_message,
            "exception_type": type(exception).__name__ if exception else None,
            "exception_message": str(exception) if exception else None,
            "http_status": http_status,
        }
        return error_dict
