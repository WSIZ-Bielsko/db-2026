import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes


def load_public_key(filepath: str):
    with open(filepath, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())


def load_private_key(filepath: str, password: bytes = None):
    with open(filepath, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=password)


def encrypt_string(public_key: PublicKeyTypes, message: str) -> str:
    ciphertext = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # Return as base64 string for easy transport/storage
    return base64.b64encode(ciphertext).decode('utf-8')


def decrypt_string(private_key: PrivateKeyTypes, b64_ciphertext: str) -> str:
    raw_ciphertext = base64.b64decode(b64_ciphertext)
    plaintext = private_key.decrypt(
        raw_ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext.decode('utf-8')


if __name__ == "__main__":
    key_dir = "keys"
    # Load keys
    pub_key: PublicKeyTypes = load_public_key(f"{key_dir}/public.pem")
    priv_key: PrivateKeyTypes = load_private_key(f"{key_dir}/private.pem")

    # Encrypt and Decrypt
    original_text = "Highly confidential system data"

    encrypted = encrypt_string(pub_key, original_text)
    # encrypted = '(paste_me_here)=='
    print(f"Encrypted (Base64): {encrypted}")

    decrypted = decrypt_string(priv_key, encrypted)
    print(f"Decrypted: {decrypted}")