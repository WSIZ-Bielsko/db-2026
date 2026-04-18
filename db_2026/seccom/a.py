import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def load_public_key(filepath: str):
    with open(filepath, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())


def load_private_key(filepath: str, password: bytes = None):
    with open(filepath, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=password)


def encrypt_string(public_key, message: str) -> str:
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


def decrypt_string(private_key, b64_ciphertext: str) -> str:
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
    pub_key = load_public_key(f"{key_dir}/public.pem")
    priv_key = load_private_key(f"{key_dir}/private.pem")

    # Encrypt and Decrypt
    original_text = "Highly confidential system data"

    # encrypted = encrypt_string(pub_key, original_text)
    encrypted = 'gE7rcz2uV/lo6/Gej0NhaeIuygaaPyAT82cph5minBr8DGv5cUA9xiWl2Ruw1/2rshUF0L5MN4p34uY7UzPNOTZVgY9dfsSasP7pPXcyj2zH5UFdSwW3GA7DxwdNZTA6Cpp+OVtNAoMKAw+SWB4mn8OTrTwnAWzCNtSPsk+HHkN5pRd8VoGaCayFPoZm6tPLqtI+pQWavpQ5ObjLNOxu9b60zG4D1jAyCHVYIUO1rXXcy/FH6aELnvp3tLanxKNx7nFUKFlAWCFmJSLyBhvxXUOeQUOvzXuQ2hlAE2I5SmsJn2r5+N6fMpLLsti+mF1UNtRxIamSH4YNPxSt7BgcZg=='
    print(f"Encrypted (Base64): {encrypted}")

    decrypted = decrypt_string(priv_key, encrypted)
    print(f"Decrypted: {decrypted}")