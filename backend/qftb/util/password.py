# from argon2 import PasswordHasher
import argon2

ph = argon2.PasswordHasher()


def hash(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except argon2.exceptions.VerifyMismatchError:
        return False
