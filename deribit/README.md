# Deribit Test API Authentication

Complete Python authentication module for Deribit's test API with support for multiple authentication methods.

## Features

✅ **Multiple Authentication Methods**
- Client Credentials (simplest)
- Client Signature (HMAC-SHA256, enhanced security)
- Refresh Token (session renewal)

✅ **Automatic Token Management**
- Token expiry checking
- Automatic refresh before expiration
- Session scope support

✅ **Production-Ready**
- Environment variable support
- Error handling
- Connection testing

## Quick Start

### 1. Get API Credentials

1. Go to [Deribit Test Environment](https://test.deribit.com)
2. Create an account (if you don't have one)
3. Navigate to Account → API
4. Create a new API key with appropriate scopes

### 2. Set Up Credentials

**Recommended: Use credentials.json file**

```bash
# Copy the template
cp credentials.json.template credentials.json

# Edit and add your credentials
nano credentials.json
```

**Format:**
```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "test_mode": true
}
```

**Alternative methods:**
- Environment variables: `export DERIBIT_CLIENT_ID="..." DERIBIT_CLIENT_SECRET="..."`
- .env file: Copy `.env.template` to `.env` and add credentials

📖 **Detailed guide:** See [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md) for all credential methods

⚠️ **Security:** Never commit credentials to Git! (Already in `.gitignore`)

### 3. Install Dependencies

```bash
pip install requests
```

### 4. Run the Example

```bash
python deribit_auth.py
```

## Usage Examples

### Basic Authentication

```python
from deribit_auth import DeribitAuth

# Credentials loaded automatically from:
# - credentials.json OR
# - Environment variables OR
# - .env file
auth = DeribitAuth(test_mode=True)

# Authenticate with client credentials
auth.authenticate_credentials(scope="trade:read_write session:my_session")

# Get headers for API requests
headers = auth.get_headers()

# Test connection
auth.test_connection()
```

### Enhanced Security with Signature

```python
# Use client signature instead of sending secret
auth = DeribitAuth(test_mode=True)
auth.authenticate_signature(scope="trade:read_write session:secure")
```

### Using with Custom Credentials

```python
# Pass credentials directly (not recommended for production)
auth = DeribitAuth(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    test_mode=True
)
auth.authenticate_credentials()
```

### Making Authenticated API Calls

```python
import requests
from deribit_auth import DeribitAuth

# Authenticate
auth = DeribitAuth(test_mode=True)
auth.authenticate_credentials(scope="trade:read_write")

# Make API call
url = "https://test.deribit.com/api/v2/private/get_positions"
params = {"currency": "BTC", "kind": "future"}

response = requests.get(url, params=params, headers=auth.get_headers())
data = response.json()

print(data)
```

### Automatic Token Refresh

```python
auth = DeribitAuth(test_mode=True)
auth.authenticate_credentials()

# Token automatically refreshes when needed
for i in range(100):
    # get_headers() will auto-refresh if token is expiring
    headers = auth.get_headers()
    # Make your API calls here
```

## Access Scopes

When authenticating, you can specify different scopes:

### Connection Management
- `connection` - Token valid for single connection only
- `session:name` - Creates named session, allows reconnection

### Functional Scopes
- `account:read` - Read account information
- `account:read_write` - Full account management
- `trade:read` - Read trading data
- `trade:read_write` - Place and manage orders
- `wallet:read` - Read wallet information
- `wallet:read_write` - Withdraw and manage wallet
- `block_trade:read_write` - Block trading access
- `block_rfq:read_write` - Block RFQ access

### Example with Multiple Scopes

```python
auth.authenticate_credentials(
    scope="trade:read_write wallet:read session:trading_bot"
)
```

## Authentication Methods Comparison

| Method | Security | Use Case | Complexity |
|--------|----------|----------|------------|
| Client Credentials | Medium | Simple bots, testing | Low |
| Client Signature | High | Production systems | Medium |
| Refresh Token | Medium | Long-running sessions | Low |

## Important Notes

### Token Lifetime
- Access tokens expire after the time specified in `expires_in` (typically 1 year for test)
- Use refresh tokens to get new access tokens without re-authentication
- The module automatically handles token refresh

### Session Limits
- Maximum 16 sessions per API key
- Maximum 32 connections per IP address
- Oldest session is removed when limit is exceeded

### Security Best Practices
- Always use environment variables for credentials
- Never commit credentials to version control
- Use session-scoped tokens for production
- Implement proper error handling

## Troubleshooting

### "Client ID and Secret required" Error
Make sure you've set the environment variables:
```bash
export DERIBIT_CLIENT_ID="your_id"
export DERIBIT_CLIENT_SECRET="your_secret"
```

### Connection Test Fails
1. Verify your credentials are correct
2. Check you're using test environment credentials on test.deribit.com
3. Ensure your API key has the required scopes

### Token Expired
The module automatically refreshes tokens. If you see this error:
- Check your system time is synchronized
- Verify the refresh token is still valid
- Re-authenticate if needed

## API Reference

### DeribitAuth Class

#### Methods

**`__init__(client_id, client_secret, test_mode=True)`**
- Initialize authentication handler
- Parameters:
  - `client_id`: API Client ID
  - `client_secret`: API Client Secret
  - `test_mode`: Use test environment (default: True)

**`authenticate_credentials(scope="session:default")`**
- Authenticate using client credentials
- Returns: Authentication response dict

**`authenticate_signature(scope="session:default", data="")`**
- Authenticate using HMAC-SHA256 signature
- Returns: Authentication response dict

**`refresh_access_token()`**
- Refresh access token using refresh token
- Returns: New authentication response dict

**`is_token_valid(buffer_seconds=60)`**
- Check if current token is valid
- Returns: Boolean

**`get_headers()`**
- Get authentication headers for HTTP requests
- Returns: Dict with Authorization header

**`test_connection()`**
- Test authentication by calling get_account_summary
- Returns: Account summary dict

## Production Deployment

For production use:

1. **Use Environment Variables**
   ```python
   auth = DeribitAuth(test_mode=False)  # Production mode
   auth.authenticate_signature()  # More secure
   ```

2. **Implement Error Handling**
   ```python
   try:
       auth.authenticate_credentials()
   except Exception as e:
       logger.error(f"Authentication failed: {e}")
       # Handle error appropriately
   ```

3. **Monitor Token Expiry**
   ```python
   if not auth.is_token_valid(buffer_seconds=300):  # 5 min buffer
       auth.refresh_access_token()
   ```

## Resources

- [Deribit API Documentation](https://docs.deribit.com/)
- [Authentication Guide](https://docs.deribit.com/articles/authentication)
- [Access Scopes](https://docs.deribit.com/articles/access-scope)
- [Test Environment](https://test.deribit.com)

## License

This code is provided as-is for educational and development purposes.

## Support

For Deribit API support:
- Documentation: https://docs.deribit.com/
- Support: https://support.deribit.com/
