#!/usr/bin/env python3
"""
Decrypt ECDH + AES encrypted messages from baby-kitty

Format: TBD - need baby-kitty to confirm encryption method
- Ciphertext is 126 bytes, no standard ECIES pubkey prefix
- They're using our public key, so ephemeral key should be embedded
- OR they're using static key exchange with custom KDF

Current attempts:
- HKDF with various info params
- SHA256 hash of shared secret
- Concat KDF (NIST SP 800-56A)
- AES-CBC and AES-GCM
- Various IV sizes (12, 16)

Baby-kitty's public key (compressed): 0213899b2f3a3a96bf9223d47d9c3c358726b4a413b095036a9daefbf2d1f06ba7
Our private key: /tmp/farclaw_ecdh.pem
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib

# Load our private key
with open('/tmp/farclaw_ecdh.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

# Baby-kitty's compressed public key (if using static key exchange)
BABY_KITTY_PUBKEY = bytes.fromhex('0213899b2f3a3a96bf9223d47d9c3c358726b4a413b095036a9daefbf2d1f06ba7')
baby_kitty_pubkey = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), BABY_KITTY_PUBKEY)

# ECDH shared secret (if static key exchange)
shared_secret_static = private_key.exchange(ec.ECDH(), baby_kitty_pubkey)
print(f"Static shared secret: {shared_secret_static.hex()}")

# Ciphertexts from baby-kitty
CIPHERTEXTS = [
    'c9gGYrpOndOuYcTib+pC8vRr+OurCn3Fv+B+7saOs1Og8Oqa5MqzYf8Sv35w5wPcH9nuEy6c4VnX5NKxJLgLfUnsoJwFzbAp0dNsNJk33k3flWY60g+Ve7dxVXVfAzonFalafLiCDLw7RYvkwde1Ds+JQYozQifGaP3rA1Wv',
    'SBSGYmreVoJgc4kLxhFBKNenFx/VckT3I9cktD4Nmlz4oszfNUarK/tE/FI5/8w3NRbhnaVfHrr3MFD0NQBcQknh7mnF0wwKwlIxDJ+AcomYvhGCbkE2U2VYxKpQnd1sW3mdwzPM/cyDxc525JFoB0K6rFoHMKgilCfkJdT9'
]

def concat_kdf(z, keydatalen, otherinfo=b''):
    """NIST SP 800-56A Concatenation KDF"""
    reps = (keydatalen + 31) // 32
    okm = b''
    for counter in range(1, reps + 1):
        okm += hashlib.sha256(counter.to_bytes(4, 'big') + z + otherinfo).digest()
    return okm[:keydatalen]

def try_decrypt(ct_bytes, key, iv_size):
    """Try AES-GCM decryption"""
    iv = ct_bytes[:iv_size]
    ct_and_tag = ct_bytes[iv_size:]
    try:
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(iv, ct_and_tag, None)
    except:
        return None

def try_decrypt_cbc(ct_bytes, key, iv_size):
    """Try AES-CBC decryption with PKCS7 unpadding"""
    iv = ct_bytes[:iv_size]
    ct = ct_bytes[iv_size:]
    try:
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ct) + decryptor.finalize()
        pad_len = padded[-1]
        if 0 < pad_len <= 16 and all(b == pad_len for b in padded[-pad_len:]):
            return padded[:-pad_len]
    except:
        pass
    return None

def derive_keys(ss):
    """Generate various key derivations to try"""
    return [
        ("HKDF('')", HKDF(hashes.SHA256(), 32, None, b'', backend=default_backend()).derive(ss)),
        ("HKDF('aes-gcm')", HKDF(hashes.SHA256(), 32, None, b'aes-gcm', backend=default_backend()).derive(ss)),
        ("HKDF('ecdh')", HKDF(hashes.SHA256(), 32, None, b'ecdh', backend=default_backend()).derive(ss)),
        ("SHA256", hashlib.sha256(ss).digest()),
        ("ConcatKDF", concat_kdf(ss, 32)),
        ("ss[:32]", ss[:32]),
    ]

print("\n=== Trying static key exchange ===")
for i, ct_b64 in enumerate(CIPHERTEXTS, 1):
    ct_bytes = base64.b64decode(ct_b64)
    print(f"\nCiphertext {i}: {len(ct_bytes)} bytes, starts with {ct_bytes[:8].hex()}")
    
    for key_name, key in derive_keys(shared_secret_static):
        for iv_size in [12, 16]:
            pt = try_decrypt(ct_bytes, key, iv_size)
            if pt:
                try:
                    print(f"✓ GCM {key_name} iv={iv_size}: {pt.decode('utf-8')}")
                except:
                    print(f"✓ GCM {key_name} iv={iv_size}: {pt}")
            
            pt = try_decrypt_cbc(ct_bytes, key, iv_size)
            if pt:
                try:
                    print(f"✓ CBC {key_name} iv={iv_size}: {pt.decode('utf-8')}")
                except:
                    print(f"✓ CBC {key_name} iv={iv_size}: {pt}")

# Try ECIES format with ephemeral key embedded
print("\n=== Trying ECIES (ephemeral key embedded) ===")
for i, ct_b64 in enumerate(CIPHERTEXTS, 1):
    ct_bytes = base64.b64decode(ct_b64)
    
    # Compressed ephemeral key (33 bytes)
    if len(ct_bytes) > 49:  # 33 + 16 (iv) minimum
        for pubkey_size in [33, 65]:
            if pubkey_size == 65 and ct_bytes[0] != 0x04:
                continue
            if pubkey_size == 33 and ct_bytes[0] not in (0x02, 0x03):
                continue
                
            ephemeral_bytes = ct_bytes[:pubkey_size]
            rest = ct_bytes[pubkey_size:]
            
            try:
                ephemeral_pubkey = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), ephemeral_bytes)
                ss = private_key.exchange(ec.ECDH(), ephemeral_pubkey)
                
                for key_name, key in derive_keys(ss):
                    for iv_size in [12, 16]:
                        pt = try_decrypt(rest, key, iv_size)
                        if pt:
                            print(f"✓ ECIES {key_name} iv={iv_size}: {pt.decode('utf-8')}")
            except:
                pass

print("\n=== No decryption succeeded ===")
print("Need to confirm encryption format with baby-kitty")
