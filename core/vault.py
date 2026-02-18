"""
Zemi Secure Vault Module
Handles encrypted credential storage and retrieval
"""

from cryptography.fernet import Fernet
import json
import os
from pathlib import Path

class SecureVault:
    def __init__(self, vault_dir):
        self.vault_dir = Path(vault_dir)
        self.master_key_path = self.vault_dir / 'master.key'
        self._cipher = None
        
    def _load_cipher(self):
        """Load encryption cipher from master key"""
        if not self.master_key_path.exists():
            raise FileNotFoundError("Master key not found. Vault access denied.")
        
        with open(self.master_key_path, 'rb') as f:
            key = f.read()
        
        self._cipher = Fernet(key)
        
    def get_credentials(self, cred_file):
        """
        Decrypt and return credentials
        Credentials only exist in memory temporarily
        """
        if self._cipher is None:
            self._load_cipher()
        
        cred_path = self.vault_dir / cred_file
        
        if not cred_path.exists():
            raise FileNotFoundError(f"Credential file {cred_file} not found")
        
        # Read encrypted data
        with open(cred_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt
        try:
            decrypted_data = self._cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode())
            return credentials
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {e}")
    
    def encrypt_and_store(self, cred_file, credentials):
        """Encrypt and store new credentials"""
        if self._cipher is None:
            self._load_cipher()
        
        cred_path = self.vault_dir / cred_file
        
        # Encrypt
        encrypted_data = self._cipher.encrypt(
            json.dumps(credentials).encode()
        )
        
        # Store with secure permissions
        with open(cred_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Set restrictive permissions
        os.chmod(cred_path, 0o600)
        
    def __del__(self):
        """Zero memory when object is destroyed"""
        self._cipher = None

# Usage example (for testing only - remove in production)
if __name__ == "__main__":
    vault = SecureVault('../vault')
    
    try:
        # Test: Load Proton credentials
        proton_creds = vault.get_credentials('proton.enc')
        print("✓ Vault access successful")
        print(f"  Username: {proton_creds['username']}")
        print(f"  IMAP: {proton_creds['imap_host']}:{proton_creds['imap_port']}")
        print(f"  SMTP: {proton_creds['smtp_host']}:{proton_creds['smtp_port']}")
        # Never print password!
        
    except Exception as e:
        print(f"✗ Vault error: {e}")
