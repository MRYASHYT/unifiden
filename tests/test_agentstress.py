import pytest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.crypto_signer import CryptoSigner
from evaluation.rubric_engine import RubricEngine

def test_crypto_signing():
    """Verifies that cryptographic signing and verification works."""
    signer = CryptoSigner(key_dir="tests/temp_keys")
    test_data = {"test": "data"}
    signature = signer.sign_data(test_data)
    assert signer.verify_signature(test_data, signature) == True
    
    # Test tampering
    test_data["test"] = "tampered"
    assert signer.verify_signature(test_data, signature) == False
    
    # Cleanup
    import shutil
    if os.path.exists("tests/temp_keys"):
        shutil.rmtree("tests/temp_keys")

def test_rubric_engine_loading():
    """Verifies that rubrics.json is correctly formatted and loadable."""
    engine = RubricEngine()
    assert len(engine.rubrics) >= 30
    assert "clear_01" in engine.rubrics
    assert "adv_10" in engine.rubrics

def test_data_presence():
    """Verifies that the generated results and figures exist."""
    assert os.path.exists("results/paper1_results.csv")
    assert os.path.exists("paper/figures/failure_rates.png")

if __name__ == "__main__":
    pytest.main([__file__])
