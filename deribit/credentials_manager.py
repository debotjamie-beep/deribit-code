"""
Deribit Credentials Manager

Securely load API credentials from multiple sources:
1. JSON file (credentials.json)
2. Environment variables
3. .env file
4. Direct input (for testing only)

Best practices:
- Never commit credentials to Git
- Use .gitignore to exclude credential files
- Prefer environment variables for production
"""

import os
import json
from typing import Dict, Optional, Tuple


class CredentialsManager:
    """
    Load Deribit API credentials securely from multiple sources
    """

    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Initialize credentials manager

        Args:
            credentials_file: Path to JSON credentials file (default: credentials.json)
        """
        self.credentials_file = credentials_file
        self.client_id = None
        self.client_secret = None

    def load_from_json(self, filepath: Optional[str] = None) -> bool:
        """
        Load credentials from JSON file

        Expected JSON format:
        {
            "client_id": "your_client_id",
            "client_secret": "your_client_secret",
            "test_mode": true
        }

        Args:
            filepath: Path to JSON file (default: credentials.json)

        Returns:
            True if successfully loaded
        """
        filepath = filepath or self.credentials_file

        try:
            if not os.path.exists(filepath):
                return False

            with open(filepath, 'r') as f:
                creds = json.load(f)

            self.client_id = creds.get('client_id')
            self.client_secret = creds.get('client_secret')

            if self.client_id and self.client_secret:
                return True
            else:
                return False

        except json.JSONDecodeError:
            return False
        except Exception:
            return False

    def load_from_env(self) -> bool:
        """
        Load credentials from environment variables

        Expected variables:
        - DERIBIT_CLIENT_ID
        - DERIBIT_CLIENT_SECRET

        Returns:
            True if successfully loaded
        """
        self.client_id = os.getenv('DERIBIT_CLIENT_ID')
        self.client_secret = os.getenv('DERIBIT_CLIENT_SECRET')

        if self.client_id and self.client_secret:
            return True
        else:
            return False

    def load_from_dotenv(self, filepath: str = ".env") -> bool:
        """
        Load credentials from .env file

        Expected .env format:
        DERIBIT_CLIENT_ID=your_client_id
        DERIBIT_CLIENT_SECRET=your_client_secret

        Args:
            filepath: Path to .env file

        Returns:
            True if successfully loaded
        """
        try:
            if not os.path.exists(filepath):
                return False

            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")

                            if key == 'DERIBIT_CLIENT_ID':
                                self.client_id = value
                            elif key == 'DERIBIT_CLIENT_SECRET':
                                self.client_secret = value

            if self.client_id and self.client_secret:
                return True
            else:
                return False

        except Exception:
            return False

    def load_interactive(self) -> bool:
        """
        Prompt user to enter credentials interactively

        Returns:
            True if credentials entered
        """
        print("\n" + "=" * 60)
        print("Enter your Deribit API credentials")
        print("=" * 60)
        print("(You can find these at: https://test.deribit.com/account/BTC/api)")
        print()

        self.client_id = input("Client ID: ").strip()
        self.client_secret = input("Client Secret: ").strip()

        if self.client_id and self.client_secret:
            print("\nCredentials entered")

            # Ask if user wants to save
            save = input("\nSave credentials to credentials.json? (y/n): ").strip().lower()
            if save == 'y':
                self.save_to_json()

            return True
        else:
            print("\nInvalid credentials")
            return False

    def save_to_json(self, filepath: Optional[str] = None) -> bool:
        """
        Save current credentials to JSON file

        Args:
            filepath: Path to save JSON file (default: credentials.json)

        Returns:
            True if successfully saved
        """
        filepath = filepath or self.credentials_file

        if not self.client_id or not self.client_secret:
            print("No credentials to save")
            return False

        try:
            creds = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "test_mode": True,
                "note": "These are your Deribit API credentials. Keep them secure!"
            }

            with open(filepath, 'w') as f:
                json.dump(creds, f, indent=2)

            print(f"Credentials saved to {filepath}")
            print(f"Remember to add '{filepath}' to .gitignore!")
            return True

        except Exception as e:
            print(f"Error saving credentials: {e}")
            return False

    def load(self, interactive: bool = False) -> Tuple[Optional[str], Optional[str]]:
        """
        Load credentials from any available source

        Priority order:
        1. JSON file (credentials.json)
        2. Environment variables
        3. .env file
        4. Interactive input (if enabled)

        Args:
            interactive: Allow interactive input if other methods fail

        Returns:
            Tuple of (client_id, client_secret) or (None, None)
        """
        # Try JSON file first
        if self.load_from_json():
            return self.client_id, self.client_secret

        # Try environment variables
        if self.load_from_env():
            return self.client_id, self.client_secret

        # Try .env file
        if self.load_from_dotenv():
            return self.client_id, self.client_secret

        # Interactive input as last resort
        if interactive:
            if self.load_interactive():
                return self.client_id, self.client_secret

        return None, None

    def get_credentials(self) -> Dict[str, Optional[str]]:
        """
        Get credentials as dictionary

        Returns:
            Dictionary with client_id and client_secret
        """
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }


def create_credentials_template():
    """
    Create a template credentials.json file
    """
    template = {
        "client_id": "YOUR_CLIENT_ID_HERE",
        "client_secret": "YOUR_CLIENT_SECRET_HERE",
        "test_mode": True,
        "notes": [
            "Get your credentials from: https://test.deribit.com/account/BTC/api",
            "NEVER commit this file to Git!",
            "Add 'credentials.json' to .gitignore"
        ]
    }

    filename = "credentials.json.template"
    with open(filename, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"Created template: {filename}")
    print(f"  1. Rename to 'credentials.json'")
    print(f"  2. Replace with your actual credentials")
    print(f"  3. Add 'credentials.json' to .gitignore")


if __name__ == "__main__":
    """
    Test the credentials manager
    """
    print("=" * 60)
    print("Deribit Credentials Manager - Test")
    print("=" * 60)
    print()

    # Test loading credentials
    manager = CredentialsManager()
    client_id, client_secret = manager.load(interactive=True)

    if client_id and client_secret:
        print("\nCredentials loaded successfully!")
        # Only print masked versions for security
        print(f"  Client ID: {client_id[:4]}{'*' * (len(client_id) - 4)}")
        print(f"  Client Secret: {'*' * len(client_secret)}")
    else:
        print("\nFailed to load credentials")
        print("\nCreating template file...")
        create_credentials_template()
