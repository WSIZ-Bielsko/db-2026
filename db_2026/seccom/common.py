from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64


def short_key(key: str):
    return key.split('\n')[1]


def generate_keypair() -> tuple[PublicKeyTypes, PrivateKeyTypes]:
    """Generate 2048-bit RSA keys and write PEM files."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # priv_pem = private_key.private_bytes(
    #     serialization.Encoding.PEM,
    #     serialization.PrivateFormat.PKCS8,
    #     serialization.NoEncryption()
    # )
    # pub_pem = public_key.public_bytes(
    #     serialization.Encoding.PEM,
    #     serialization.PublicFormat.SubjectPublicKeyInfo
    # )

    return public_key, private_key


# I/O

def load_public_key(filepath: str):
    with open(filepath, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())


def load_private_key(filepath: str, password: bytes = None):
    with open(filepath, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=password)

def write_private_key(key: PrivateKeyTypes, filepath: str):
    with open(filepath, "wb") as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        ))

def write_public_key(key: PublicKeyTypes, filepath: str):
    with open(filepath, "wb") as f:
        f.write(key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def public_to_string(key: PublicKeyTypes) -> str:
    return key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

def public_from_string(data: str) -> PublicKeyTypes:
    return serialization.load_pem_public_key(data.encode('utf-8'))


# text operations

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
