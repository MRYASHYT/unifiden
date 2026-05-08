import json
import hashlib
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
import os
import shutil
from agentstress.config import Config

# Configure logging
# ... (rest of imports)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CryptoSigner:
    """
    Handles cryptographic signing and verification for AgentStress reports.
    Provides the foundation for 'Above Industry Standard' trust and transparency.
    """
    
    def __init__(self, key_dir: str = "security/keys"):
        self.key_dir = key_dir
        self.private_key_path = os.path.join(key_dir, "private_key.pem")
        self.public_key_path = os.path.join(key_dir, "public_key.pem")
        # Define passphrase from environment variable for enterprise security.
        self.passphrase = Config.KEY_PASS.encode()
        
        if not os.path.exists(self.key_dir):
            os.makedirs(self.key_dir)

    def generate_keys(self):
        """Generates a new RSA key pair for the local environment."""
        logger.info("Generating new RSA-4096 key pair.")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )
        
        # Serialize private key with BestAvailableEncryption
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(self.passphrase)
        )
        
        # Serialize public key
        pem_public = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(self.private_key_path, "wb") as f:
            f.write(pem_private)
            
        with open(self.public_key_path, "wb") as f:
            f.write(pem_public)
            
        logger.info(f"Keys generated and stored in {self.key_dir}")
        return self.public_key_path

    def rotate_keys(self):
        """Rotates the cryptographic keys by backing up the old ones and generating new ones."""
        logger.info("Rotating cryptographic keys.")
        if os.path.exists(self.private_key_path) or os.path.exists(self.public_key_path):
            backup_dir = os.path.join(self.key_dir, f"backup_{int(os.path.getmtime(self.private_key_path))}")
            os.makedirs(backup_dir, exist_ok=True)
            if os.path.exists(self.private_key_path):
                shutil.copy(self.private_key_path, os.path.join(backup_dir, "private_key.pem"))
            if os.path.exists(self.public_key_path):
                shutil.copy(self.public_key_path, os.path.join(backup_dir, "public_key.pem"))
            logger.info(f"Old keys backed up to {backup_dir}")
        
        self.generate_keys()

    def load_private_key(self):
        with open(self.private_key_path, "rb") as key_file:
            key_data = key_file.read()
            try:
                # Try loading with passphrase
                return serialization.load_pem_private_key(
                    key_data,
                    password=self.passphrase,
                )
            except (TypeError, ValueError):
                # Fallback: Try loading without passphrase (for old/unencrypted keys)
                logger.warning("Private key not encrypted or passphrase incorrect. Attempting unencrypted load.")
                return serialization.load_pem_private_key(
                    key_data,
                    password=None,
                )

    def load_public_key(self):
        with open(self.public_key_path, "rb") as key_file:
            return serialization.load_pem_public_key(
                key_file.read()
            )

    def sign_data(self, data: dict) -> str:
        """
        Hashes the dictionary data and signs it with the private key.
        Returns the signature as a hex string.
        """
        if not os.path.exists(self.private_key_path):
            self.generate_keys()
            
        private_key = self.load_private_key()
        
        # Canonicalize JSON to ensure consistent hashing
        data_string = json.dumps(data, sort_keys=True).encode('utf-8')
        
        signature = private_key.sign(
            data_string,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature.hex()

    def verify_signature(self, data: dict, signature_hex: str) -> bool:
        """
        Verifies the signature against the provided data and the local public key.
        """
        public_key = self.load_public_key()
        try:
            signature = bytes.fromhex(signature_hex)
        except ValueError as e:
            logger.error(f"Invalid signature format: {e}")
            return False

        data_string = json.dumps(data, sort_keys=True).encode('utf-8')
        
        try:
            public_key.verify(
                signature,
                data_string,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
            return False

if __name__ == "__main__":
    # Quick test
    signer = CryptoSigner()
    # Force generate keys to test BestAvailableEncryption
    signer.generate_keys()
    test_data = {"test": "data", "result": 100}
    sig = signer.sign_data(test_data)
    print(f"Generated Signature: {sig}")
    is_valid = signer.verify_signature(test_data, sig)
    print(f"Is valid: {is_valid}")
    
    # Test tampering
    test_data["result"] = 101
    is_valid_tampered = signer.verify_signature(test_data, sig)
    print(f"Is valid after tampering: {is_valid_tampered}")
    
    # Test key rotation
    signer.rotate_keys()
