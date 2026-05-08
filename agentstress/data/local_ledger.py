import json
import os
import time
from typing import Dict, Any, List
from agentstress.security.crypto_signer import CryptoSigner
from agentstress.config import Config

class LocalLedger:
    """
    Handles secure, cryptographically signed storage of evaluation results.
    Provides the foundation for 'Above Industry Standard' transparency.
    """
    
    def __init__(self, ledger_file: str = None):
        self.ledger_file = ledger_file or Config.LEDGER_FILE
        self.signer = CryptoSigner()
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)

    def record_entry(self, result_data: Dict[str, Any]) -> str:
        """
        Signs the result data and appends it to the ledger.
        This provides a tamper-evident audit trail for all AI evaluations.
        
        Args:
            result_data: Dictionary containing evaluation results.
            
        Returns:
            The cryptographic signature of the entry.
        """
        # 1. Sign the data
        signature = self.signer.sign_data(result_data)
        
        # 2. Create the ledger entry
        entry = {
            "timestamp": time.time(),
            "data": result_data,
            "signature": signature,
            "public_key_path": self.signer.public_key_path
        }
        
        # 3. Append to JSONL file
        with open(self.ledger_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        return signature

    def get_recent_entries(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves the last N entries from the ledger.
        
        Args:
            n: Number of entries to retrieve.
            
        Returns:
            List of ledger entries.
        """
        entries = []
        if not os.path.exists(self.ledger_file):
            return entries
            
        with open(self.ledger_file, "r") as f:
            lines = f.readlines()
            for line in lines[-n:]:
                entries.append(json.loads(line))
        return entries

    def verify_ledger(self) -> bool:
        """
        Iterates through the ledger and verifies every signature.
        """
        if not os.path.exists(self.ledger_file):
            return True
            
        with open(self.ledger_file, "r") as f:
            for line in f:
                entry = json.loads(line)
                data = entry["data"]
                signature = entry["signature"]
                
                if not self.signer.verify_signature(data, signature):
                    return False
        return True

if __name__ == "__main__":
    # Test Ledger
    ledger = LocalLedger()
    test_result = {
        "agent_id": "test_agent",
        "score": 95,
        "failure_mode": "NO_FAILURE"
    }
    sig = ledger.record_entry(test_result)
    print(f"Record added with signature: {sig}")
    print(f"Ledger verified: {ledger.verify_ledger()}")
