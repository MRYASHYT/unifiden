import json
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
import os

class CryptoSigner:
    """
    Handles cryptographic signing and verification for AgentStress reports.
    Provides the foundation for 'Above Industry Standard' trust and transparency.
    """
    
    def __init__(self, key_dir: str = "security/keys"):
        self.key_dir = key_dir
        self.private_key_path = os.path.join(key_dir, "private_key.pem")
        self.public_key_path = os.path.join(key_dir, "public_key.pem")
        
        if not os.path.exists(self.key_dir):
            os.makedirs(self.key_dir)

    def generate_keys(self):
        """Generates a new RSA key pair for the local environment."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        )
        
        # Serialize private key
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
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
            
        return self.public_key_path

    def load_private_key(self):
        with open(self.private_key_path, "rb") as key_file:
            return serialization.load_pem_private_key(
                key_file.read(),
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
        signature = bytes.fromhex(signature_hex)
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
        except Exception:
            return False

if __name__ == "__main__":
    # Quick test
    signer = CryptoSigner()
    test_data = {"test": "data", "result": 100}
    sig = signer.sign_data(test_data)
    print(f"Generated Signature: {sig}")
    is_valid = signer.verify_signature(test_data, sig)
    print(f"Is valid: {is_valid}")
    
    # Test tampering
    test_data["result"] = 101
    is_valid_tampered = signer.verify_signature(test_data, sig)
    print(f"Is valid after tampering: {is_valid_tampered}")
