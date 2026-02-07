# 🔐 Credentials Setup Guide

## Overview

This package supports **multiple secure ways** to provide your Deribit API credentials. Choose the method that best fits your workflow!

## ✅ Recommended: credentials.json File

**Best for:** Local development, easy setup, multiple projects

### Step 1: Create credentials.json

Copy the template:
```bash
cp credentials.json.template credentials.json
```

Or create manually:
```json
{
  "client_id": "YOUR_CLIENT_ID_HERE",
  "client_secret": "YOUR_CLIENT_SECRET_HERE",
  "test_mode": true
}
```

### Step 2: Add Your Credentials

1. Go to https://test.deribit.com/account/BTC/api
2. Click "Add new key"
3. Select scopes (e.g., trade:read_write)
4. Copy the Client ID and Secret
5. Paste them into `credentials.json`

### Step 3: Verify Setup

```bash
python test_with_credentials.py
```

### ✅ Advantages
- Simple to set up
- Easy to edit
- One file per project
- Clear structure

### ⚠️ Security Notes
- **NEVER commit credentials.json to Git!**
- Already listed in `.gitignore` for safety
- Keep file permissions restricted: `chmod 600 credentials.json`

---

## 🌍 Alternative: Environment Variables

**Best for:** Production, CI/CD, Docker, shared systems

### Linux/macOS

```bash
export DERIBIT_CLIENT_ID="your_client_id"
export DERIBIT_CLIENT_SECRET="your_client_secret"
```

Make permanent by adding to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export DERIBIT_CLIENT_ID="your_id"' >> ~/.bashrc
echo 'export DERIBIT_CLIENT_SECRET="your_secret"' >> ~/.bashrc
source ~/.bashrc
```

### Windows

**Command Prompt:**
```cmd
set DERIBIT_CLIENT_ID=your_client_id
set DERIBIT_CLIENT_SECRET=your_client_secret
```

**PowerShell:**
```powershell
$env:DERIBIT_CLIENT_ID="your_client_id"
$env:DERIBIT_CLIENT_SECRET="your_client_secret"
```

**Permanent (Windows):**
1. Search "Environment Variables" in Start Menu
2. Click "Edit system environment variables"
3. Click "Environment Variables"
4. Add new variables

### ✅ Advantages
- Secure (not in code or files)
- Good for production
- Works across projects

### ⚠️ Considerations
- Need to set on each system
- Can be forgotten after restart (unless made permanent)

---

## 📄 Alternative: .env File

**Best for:** Multiple environments, team projects, 12-factor apps

### Step 1: Create .env File

Copy the template:
```bash
cp .env.template .env
```

Or create manually:
```bash
DERIBIT_CLIENT_ID=your_client_id
DERIBIT_CLIENT_SECRET=your_client_secret
```

### Step 2: Add Credentials

Edit `.env` and replace with your actual credentials.

### Step 3: Use in Code

The package will automatically load `.env` file.

### ✅ Advantages
- Popular standard (12-factor app)
- Works with many tools
- Easy to switch environments

### ⚠️ Security Notes
- **NEVER commit .env to Git!**
- Already listed in `.gitignore`

---

## 💻 Alternative: Direct in Code

**Best for:** Quick tests, prototypes (NOT for production!)

```python
from deribit_auth import DeribitAuth

auth = DeribitAuth(
    client_id="your_client_id",
    client_secret="your_client_secret",
    test_mode=True
)
```

### ⚠️ WARNING
- **NEVER commit code with credentials!**
- Only use for quick local tests
- Not recommended for production

---

## 🔄 Priority Order

The package tries to load credentials in this order:

1. **Direct parameters** (if provided)
2. **credentials.json** file
3. **Environment variables**
4. **.env** file

If none are found, you'll get a helpful error message.

---

## 🧪 Testing Your Setup

After setting up credentials, test with:

```bash
# Run full test
python test_with_credentials.py

# Or use Python directly
python -c "from deribit_auth import DeribitAuth; auth = DeribitAuth(); print('✓ Credentials loaded!')"
```

---

## 📋 Comparison Table

| Method | Setup Time | Security | Portability | Production Ready |
|--------|------------|----------|-------------|------------------|
| **credentials.json** | ⭐⭐⭐ Fast | ⭐⭐ Good | ⭐⭐ Medium | ✅ Yes |
| **Environment Vars** | ⭐⭐ Medium | ⭐⭐⭐ Best | ⭐⭐⭐ High | ✅ Yes |
| **.env File** | ⭐⭐⭐ Fast | ⭐⭐ Good | ⭐⭐⭐ High | ✅ Yes |
| **Direct in Code** | ⭐⭐⭐ Instant | ⭐ Poor | ⭐ Low | ❌ No |

---

## 🛡️ Security Best Practices

### ✅ DO:
- Use credentials.json or .env for development
- Use environment variables for production
- Keep credentials file permissions restricted
- Use different credentials for test and production
- Regularly rotate your API keys

### ❌ DON'T:
- Commit credentials to Git
- Share credentials in chat/email
- Use production credentials for testing
- Hardcode credentials in source files
- Leave credentials in screenshot/logs

---

## 🔍 Troubleshooting

### "Credentials required" Error

**Problem:** No credentials found

**Solution:** 
1. Check credentials.json exists and has correct format
2. Verify environment variables are set: `echo $DERIBIT_CLIENT_ID`
3. Check .env file exists and has correct format
4. Make sure you're in the correct directory

### "Authentication failed" Error

**Problem:** Credentials are incorrect or invalid

**Solution:**
1. Verify credentials at https://test.deribit.com/account/BTC/api
2. Check for copy/paste errors (spaces, newlines)
3. Ensure API key has correct scopes enabled
4. Try regenerating the API key

### credentials.json Not Loading

**Problem:** File exists but not being read

**Solution:**
1. Check file name exactly: `credentials.json` (not `.txt`, not template)
2. Verify JSON format is valid (use https://jsonlint.com/)
3. Check file is in the same directory as your script
4. Verify file permissions: `ls -la credentials.json`

---

## 📝 Example Files

### credentials.json
```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "test_mode": true,
  "notes": "Test environment credentials"
}
```

### .env
```bash
# Deribit Test API Credentials
DERIBIT_CLIENT_ID=YOUR_CLIENT_ID
DERIBIT_CLIENT_SECRET=YOUR_CLIENT_SECRET

# Optional
DERIBIT_TEST_MODE=true
```

---

## 🎯 Quick Setup (Recommended)

**For most users, we recommend the credentials.json method:**

```bash
# 1. Copy template
cp credentials.json.template credentials.json

# 2. Edit and add your credentials
nano credentials.json  # or vim, code, etc.

# 3. Test
python test_with_credentials.py

# Done! ✅
```

---

## 📞 Getting Your Credentials

1. Visit: https://test.deribit.com/account/BTC/api
2. Click "Add new key"
3. Configure:
   - **Name**: Give it a name (e.g., "Trading Bot")
   - **Scopes**: Select permissions needed
     - ✅ `trade:read_write` (for trading)
     - ✅ `account:read` (for account info)
     - ✅ `wallet:read` (for balance)
4. Click "Create"
5. **Copy both**:
   - Client ID
   - Client Secret (shown only once!)
6. Save to credentials.json or environment variables

---

## 🔗 Related Documentation

- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [SKILL.md](SKILL.md) - Claude agent integration

---

## ✅ Checklist

Setup your credentials:
- [ ] Obtained API key from Deribit
- [ ] Chose a credentials method
- [ ] Set up credentials.json OR environment variables OR .env file
- [ ] Added credentials.json or .env to .gitignore (already done!)
- [ ] Tested with `python test_with_credentials.py`
- [ ] Credentials working ✅

Ready to trade! 🚀
