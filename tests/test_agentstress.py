import pytest
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentstress.security.crypto_signer import CryptoSigner
from agentstress.evaluation.rubric_engine import RubricEngine


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


@pytest.mark.skipif(
    not os.path.exists("results/paper1_results.csv"),
    reason="No experimental data generated yet — run paper1_runner.py first",
)
def test_data_presence():
    """Verifies that the generated results and figures exist after an experiment run."""
    assert os.path.exists("results/paper1_results.csv")


@pytest.mark.skipif(
    not os.path.exists("paper/figures/failure_rates.png"),
    reason="No figures generated yet — run paper_figures.py first",
)
def test_figures_presence():
    """Verifies that research figures have been generated."""
    assert os.path.exists("paper/figures/failure_rates.png")


if __name__ == "__main__":
    pytest.main([__file__])
