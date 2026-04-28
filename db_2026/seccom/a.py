import os

from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from dotenv import load_dotenv
from loguru import logger

from db_2026.seccom.common import generate_keypair, load_public_key, load_private_key, encrypt_string, decrypt_string

if __name__ == "__main__":
    load_dotenv()
    a = os.environ.get("A")
    logger.warning(f"A: {a}")

    generate_keypair('keys/first')


    key_dir = "keys"
    # Load keys
    pub_key: PublicKeyTypes = load_public_key(f"{key_dir}/first.public.pem")
    priv_key: PrivateKeyTypes = load_private_key(f"{key_dir}/first.private.pem")

    # Encrypt and Decrypt
    original_text = "Highly confidential system data"

    encrypted = encrypt_string(pub_key, original_text)
    # encrypted = '(paste_me_here)=='
    print(f"Encrypted (Base64): {encrypted}")

    decrypted = decrypt_string(priv_key, encrypted)
    print(f"Decrypted: {decrypted}")