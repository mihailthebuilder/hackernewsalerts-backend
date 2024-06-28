from cryptography.fernet import Fernet
import base64

from socialalerts.settings import SECRET_KEY


def str_to_byte(input: str) -> bytes:
    return base64.urlsafe_b64decode(input.encode())


class Tokenizer:
    def __init__(self, secret_key: str):
        self.algo = Fernet(str_to_byte(secret_key))

    def encrypt(self, input: str) -> str:
        return self.algo.encrypt(str_to_byte(input)).hex()

    def decrypt(self, input: str) -> str:
        return self.algo.decrypt(str_to_byte(input)).hex()


# tokenizer = Tokenizer(SECRET_KEY)
