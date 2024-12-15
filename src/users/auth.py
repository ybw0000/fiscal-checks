import hashlib


class Hasher:

    @staticmethod
    def hash_password(plain_password: str) -> str:
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
