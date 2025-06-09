from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from hashlib import sha256
from database import get_key_for_satellite

# Funkcja do obliczania skrótu SHA-256
def hash(data: bytes) -> bytes:
    return sha256(data).digest()

# Generowanie HMAC
def generate_hmac(nonce: bytes, key: bytes) -> bytes:
    h = hmac.HMAC(key, hashes.SHA256())
    h.update(nonce)
    return h.finalize()

# Weryfikacja HMAC
def verify_hmac(satellite_id: str, nonce: bytes, received_hmac: bytes) -> bool:
    key = get_key_for_satellite(satellite_id)
    if not key:
        return False
    expected_hmac = generate_hmac(nonce, key)
    return expected_hmac == received_hmac

# ECDH i klucze sesyjne
def generate_ecdh_key_pair():
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key

# Wymiana kluczy ECDH
def compute_shared_secret(private_key, peer_public_key):
    return private_key.exchange(peer_public_key)

def derive_session_keys(shared_secret: bytes):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=64,
        salt=None,
        info=b"satellite-key-derivation",
    )
    keys = hkdf.derive(shared_secret)
    return keys[:32], keys[32:64]  # ChaCha20, Poly1305