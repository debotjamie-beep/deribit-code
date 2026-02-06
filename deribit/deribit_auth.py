"""
Deribit Test API Authentication Module

This module provides multiple authentication methods for the Deribit test API:
- Client Credentials (simplest)
- Client Signature (enhanced security)
- Refresh Token (session renewal)

Credentials can be loaded from:
- credentials.json file
- Environment variables
- .env file
- Direct parameters

Author: API Developer
Environment: Deribit Test (test.deribit.com)
"""

import os
import time
import hmac
import hashlib
import random
import string
import requests
from typing import Optional, Dict, Any

# Try to import credentials manager (optional)
try:
    from credentials_manager import CredentialsManager
    CREDENTIALS_MANAGER_AVAILABLE = True
except ImportError:
    CREDENTIALS_MANAGER_AVAILABLE = False


class DeribitAuth:
    """
    Deribit API Authentication Handler
    
    Supports multiple authentication methods:
    - Client Credentials
    - Client Signature (HMAC-SHA256)
    - Refresh Token
    """
    
    def __init__(
        self, 
        client_id: Optional[str] = None, 
        client_secret: Optional[str] = None,
        test_mode: bool = True,
        credentials_file: Optional[str] = None
    ):
        """
        Initialize Deribit Authentication
        
        Credentials are loaded in this priority order:
        1. Direct parameters (client_id, client_secret)
        2. credentials.json file (or custom path via credentials_file)
        3. Environment variables (DERIBIT_CLIENT_ID, DERIBIT_CLIENT_SECRET)
        4. .env file
        
        Args:
            client_id: Your Deribit API Client ID (optional if using other methods)
            client_secret: Your Deribit API Client Secret (optional if using other methods)
            test_mode: Use test environment (default: True)
            credentials_file: Custom path to credentials JSON file
        """
        # Try to load credentials from various sources
        if client_id and client_secret:
            # Direct parameters provided
            self.client_id = client_id
            self.client_secret = client_secret
        elif CREDENTIALS_MANAGER_AVAILABLE:
            # Use credentials manager
            manager = CredentialsManager(credentials_file or "credentials.json")
            self.client_id, self.client_secret = manager.load(interactive=False)
        else:
            # Fall back to environment variables
            self.client_id = client_id or os.getenv('DERIBIT_CLIENT_ID')
            self.client_secret = client_secret or os.getenv('DERIBIT_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Credentials required! Provide them via:\n"
                "1. Parameters: DeribitAuth(client_id='...', client_secret='...')\n"
                "2. credentials.json file (see credentials.json.template)\n"
                "3. Environment variables: DERIBIT_CLIENT_ID and DERIBIT_CLIENT_SECRET\n"
                "4. .env file (see .env.template)\n\n"
                "See README.md for detailed setup instructions."
            )
        
        self.base_url = "https://test.deribit.com" if test_mode else "https://www.deribit.com"
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.scope = None
        
    def _generate_nonce(self, length: int = 8) -> str:
        """Generate random nonce for signature authentication"""
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    
    def _calculate_signature(
        self, 
        timestamp: int, 
        nonce: str, 
        data: str = ""
    ) -> str:
        """
        Calculate HMAC-SHA256 signature for WebSocket-style authentication
        
        Formula: StringToSign = Timestamp + "\n" + Nonce + "\n" + Data
                 Signature = HEX(HMAC-SHA256(ClientSecret, StringToSign))
        
        Args:
            timestamp: Current time in milliseconds
            nonce: Random nonce string
            data: Optional data field
            
        Returns:
            Hex-encoded HMAC-SHA256 signature
        """
        string_to_sign = f"{timestamp}\n{nonce}\n{data}"
        
        signature = hmac.new(
            self.client_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def authenticate_credentials(self, scope: str = "session:default") -> Dict[str, Any]:
        """
        Authenticate using Client Credentials (simplest method)
        
        Args:
            scope: Access scope (default: "session:default")
                   Options: "connection", "session:name", "trade:read_write", etc.
        
        Returns:
            Authentication response with access_token and refresh_token
        """
        url = f"{self.base_url}/api/v2/public/auth"
        
        params = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": scope
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        
        if "result" in result:
            self.access_token = result["result"]["access_token"]
            self.refresh_token = result["result"]["refresh_token"]
            self.token_expiry = time.time() + result["result"]["expires_in"]
            self.scope = result["result"]["scope"]
            
            print(f"✓ Authenticated successfully")
            print(f"  Scope: {self.scope}")
            print(f"  Expires in: {result['result']['expires_in']} seconds")
            
            return result["result"]
        else:
            raise Exception(f"Authentication failed: {result}")
    
    def authenticate_signature(self, scope: str = "session:default", data: str = "") -> Dict[str, Any]:
        """
        Authenticate using Client Signature (enhanced security)
        
        This method uses HMAC-SHA256 signature instead of sending the secret directly.
        
        Args:
            scope: Access scope
            data: Optional data field for signature
            
        Returns:
            Authentication response with access_token and refresh_token
        """
        url = f"{self.base_url}/api/v2/public/auth"
        
        timestamp = int(time.time() * 1000)  # milliseconds
        nonce = self._generate_nonce()
        signature = self._calculate_signature(timestamp, nonce, data)
        
        params = {
            "grant_type": "client_signature",
            "client_id": self.client_id,
            "timestamp": timestamp,
            "nonce": nonce,
            "data": data,
            "signature": signature,
            "scope": scope
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        
        if "result" in result:
            self.access_token = result["result"]["access_token"]
            self.refresh_token = result["result"]["refresh_token"]
            self.token_expiry = time.time() + result["result"]["expires_in"]
            self.scope = result["result"]["scope"]
            
            print(f"✓ Authenticated with signature")
            print(f"  Scope: {self.scope}")
            print(f"  Expires in: {result['result']['expires_in']} seconds")
            
            return result["result"]
        else:
            raise Exception(f"Authentication failed: {result}")
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh access token using refresh_token
        
        Returns:
            New authentication response with fresh tokens
        """
        if not self.refresh_token:
            raise Exception("No refresh token available. Authenticate first.")
        
        url = f"{self.base_url}/api/v2/public/auth"
        
        params = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        
        if "result" in result:
            self.access_token = result["result"]["access_token"]
            self.refresh_token = result["result"]["refresh_token"]
            self.token_expiry = time.time() + result["result"]["expires_in"]
            
            print(f"✓ Token refreshed")
            print(f"  Expires in: {result['result']['expires_in']} seconds")
            
            return result["result"]
        else:
            raise Exception(f"Token refresh failed: {result}")
    
    def is_token_valid(self, buffer_seconds: int = 60) -> bool:
        """
        Check if current access token is still valid
        
        Args:
            buffer_seconds: Refresh token if expiring within this time
            
        Returns:
            True if token is valid and not expiring soon
        """
        if not self.access_token or not self.token_expiry:
            return False
        
        return time.time() < (self.token_expiry - buffer_seconds)
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for HTTP requests
        
        Returns:
            Dictionary with Authorization header
        """
        if not self.is_token_valid():
            if self.refresh_token:
                self.refresh_access_token()
            else:
                raise Exception("Token expired and no refresh token available")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the authentication by calling a private endpoint
        
        Returns:
            Account summary or error
        """
        url = f"{self.base_url}/api/v2/private/get_account_summary"
        params = {"currency": "BTC", "extended": "true"}
        
        response = requests.get(url, params=params, headers=self.get_headers())
        response.raise_for_status()
        
        result = response.json()
        
        if "result" in result:
            print(f"\n✓ Connection test successful!")
            print(f"  Currency: {result['result'].get('currency', 'N/A')}")
            print(f"  Balance: {result['result'].get('balance', 'N/A')}")
            return result["result"]
        else:
            raise Exception(f"Connection test failed: {result}")


def main():
    """
    Example usage of DeribitAuth class
    """
    print("=" * 60)
    print("Deribit Test API Authentication Demo")
    print("=" * 60)
    
    # Initialize auth (reads from environment variables)
    auth = DeribitAuth(test_mode=True)
    
    # Method 1: Client Credentials (simplest)
    print("\n[Method 1] Client Credentials Authentication")
    print("-" * 60)
    auth.authenticate_credentials(scope="trade:read_write session:demo")
    
    # Test the connection
    print("\n[Testing Connection]")
    print("-" * 60)
    try:
        auth.test_connection()
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
    
    # Method 2: Client Signature (more secure)
    print("\n[Method 2] Client Signature Authentication")
    print("-" * 60)
    auth2 = DeribitAuth(test_mode=True)
    auth2.authenticate_signature(scope="trade:read_write session:signature_demo")
    
    # Method 3: Refresh Token
    print("\n[Method 3] Token Refresh")
    print("-" * 60)
    print(f"Token valid: {auth.is_token_valid()}")
    auth.refresh_access_token()
    
    print("\n" + "=" * 60)
    print("Authentication demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Set your credentials as environment variables:
    # export DERIBIT_CLIENT_ID="your_client_id"
    # export DERIBIT_CLIENT_SECRET="your_client_secret"
    
    main()
