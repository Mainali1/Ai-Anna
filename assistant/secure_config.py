import keyring
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
from typing import Any, Dict, Optional

class SecureConfig:
    def __init__(self, app_name: str = 'AI-Anna'):
        self.app_name = app_name
        self._encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self._encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create an encryption key using keyring."""
        key = keyring.get_password(self.app_name, 'encryption_key')
        if not key:
            # Generate a new key
            salt = b'ai-anna-salt'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(b'default-key'))
            keyring.set_password(self.app_name, 'encryption_key', key.decode())
        return key.encode() if isinstance(key, str) else key
    
    def store_secret(self, key: str, value: str) -> None:
        """Securely store a secret value."""
        encrypted = self.fernet.encrypt(value.encode())
        keyring.set_password(self.app_name, key, encrypted.decode())
    
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret value."""
        encrypted = keyring.get_password(self.app_name, key)
        if encrypted:
            try:
                decrypted = self.fernet.decrypt(encrypted.encode())
                return decrypted.decode()
            except Exception:
                return None
        return None
    
    def store_encrypted_config(self, config: Dict[str, Any], filename: str) -> None:
        """Store configuration data in an encrypted file."""
        encrypted = self.fernet.encrypt(json.dumps(config).encode())
        with open(filename, 'wb') as f:
            f.write(encrypted)
    
    def load_encrypted_config(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load configuration data from an encrypted file."""
        try:
            with open(filename, 'rb') as f:
                encrypted = f.read()
            decrypted = self.fernet.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception:
            return None
    
    def remove_secret(self, key: str) -> None:
        """Remove a stored secret."""
        try:
            keyring.delete_password(self.app_name, key)
        except keyring.errors.PasswordDeleteError:
            pass