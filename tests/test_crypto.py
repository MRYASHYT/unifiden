import pytest
import os
import shutil
from agentstress.security.crypto_signer import CryptoSigner

@pytest.fixture
def signer():
    key_dir = "tests/test_keys"
    s = CryptoSigner(key_dir=key_dir)
    # Provide passphrase explicitly for testing via monkeypatch or directly if code allows
    # In crypto_signer, passphrase is b"agentstress_secure_passphrase"
    s.generate_keys()
    yield s
    if os.path.exists(key_dir):
        shutil.rmtree(key_dir)

def test_sign_and_verify(signer):
    data = {"score": 100, "agent": "test"}
    sig = signer.sign_data(data)
    assert signer.verify_signature(data, sig) is True

def test_tamper_detection(signer):
    data = {"score": 100, "agent": "test"}
    sig = signer.sign_data(data)
    
    # Tamper with data
    tampered_data = {"score": 0, "agent": "test"}
    assert signer.verify_signature(tampered_data, sig) is False

def test_invalid_signature_format(signer):
    data = {"score": 100}
    assert signer.verify_signature(data, "invalid_hex_string_xyz") is False

def test_key_rotation(signer):
    data = {"score": 50}
    sig1 = signer.sign_data(data)
    assert signer.verify_signature(data, sig1) is True
    
    signer.rotate_keys()
    
    # Old signature might fail to verify if key changed (unless old keys are kept, but verify uses current load_public_key)
    # The new public key will not verify the old signature
    assert signer.verify_signature(data, sig1) is False
