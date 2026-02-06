# GitHub Upload Guide - Deribit Skill

## Option 1: Upload via GitHub Web Interface (Easiest)

### Step 1: Create Repository

1. Go to https://github.com/new
2. Repository name: `claude-agent-skills` (or your preferred name)
3. Description: "Skills for Claude agents"
4. Choose Public or Private
5. Click "Create repository"

### Step 2: Upload Files

1. Click "uploading an existing file"
2. Drag and drop the entire `deribit` folder
3. Or click "choose your files" and select all files from the deribit folder:
   - `__init__.py`
   - `deribit_auth.py`
   - `deribit_trader.py`
   - `simple_example.py`
   - `test_with_credentials.py`
   - `authentication_demo.py`
   - `SKILL.md`
   - `README.md`
   - `requirements.txt`
   - `.gitignore`
4. Commit message: "Add Deribit trading skill"
5. Click "Commit changes"

## Option 2: Upload via Git Command Line

### Step 1: Install Git

```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt-get install git

# Windows
# Download from https://git-scm.com/download/win
```

### Step 2: Configure Git (First Time Only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Create Repository on GitHub

1. Go to https://github.com/new
2. Create repository (don't initialize with README)
3. Copy the repository URL

### Step 4: Upload Files

```bash
# Navigate to the deribit folder
cd /path/to/deribit

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Add Deribit trading skill for Claude agents"

# Add remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 5: Authenticate (if needed)

GitHub may ask for authentication:
- Use Personal Access Token (recommended)
- Go to: Settings → Developer settings → Personal access tokens → Generate new token
- Select scopes: `repo` (full control of private repositories)
- Copy the token and use it as your password when pushing

## Option 3: Upload via GitHub Desktop (GUI)

1. Download GitHub Desktop: https://desktop.github.com/
2. Install and sign in to GitHub
3. Click "Create a New Repository on your hard drive"
4. Choose location and name
5. Copy all files from `deribit` folder to the new repository folder
6. Click "Commit to main"
7. Click "Publish repository"

## Repository Structure

Your repository should look like this:

```
your-repo/
└── deribit/
    ├── __init__.py
    ├── deribit_auth.py
    ├── deribit_trader.py
    ├── simple_example.py
    ├── test_with_credentials.py
    ├── authentication_demo.py
    ├── SKILL.md
    ├── README.md
    ├── requirements.txt
    └── .gitignore
```

## Using as Claude Agent Skill

Once uploaded to GitHub, you can use it as a skill:

### Method 1: Direct Import

```python
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Navigate to the skill
cd YOUR_REPO/deribit

# Use in your agent
from deribit import DeribitAuth, DeribitTrader
```

### Method 2: Install as Package

```bash
# Install directly from GitHub
pip install git+https://github.com/YOUR_USERNAME/YOUR_REPO.git#subdirectory=deribit
```

### Method 3: As Git Submodule

```bash
# In your agent project
git submodule add https://github.com/YOUR_USERNAME/YOUR_REPO.git skills/deribit
```

## Sharing Your Repository

After uploading, share your repository URL:
```
https://github.com/YOUR_USERNAME/YOUR_REPO/tree/main/deribit
```

## Updating the Skill

To update after making changes:

```bash
cd deribit
git add .
git commit -m "Update: description of changes"
git push
```

## Important Security Notes

⚠️ **NEVER commit your API credentials to GitHub!**

The `.gitignore` file is configured to exclude:
- `.env` files
- Credential files
- API keys

Always use environment variables for sensitive data.

## Next Steps

1. Upload to GitHub using one of the methods above
2. Test the skill by cloning and running examples
3. Share the repository URL with your Claude agent
4. Consider adding more skills to the repository

## Troubleshooting

### "Permission denied (publickey)"
- Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
- Add to GitHub: Settings → SSH keys → New SSH key

### "Repository not found"
- Check repository URL
- Ensure you have access to the repository
- Try using HTTPS instead of SSH

### "Authentication failed"
- Use Personal Access Token instead of password
- Generate token at: Settings → Developer settings → Personal access tokens

## Resources

- GitHub Documentation: https://docs.github.com/
- Git Documentation: https://git-scm.com/doc
- GitHub Desktop: https://desktop.github.com/
