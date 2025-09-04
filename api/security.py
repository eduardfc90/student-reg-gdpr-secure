# api/security.py
import os
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from passlib.hash import bcrypt

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _fernet() -> Fernet:
    key = os.getenv("FERNET_KEY")
    if not key:
        raise RuntimeError("Missing FERNET_KEY in environment (.env)")
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)

def encrypt(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet().encrypt(value.encode()).decode()

def decrypt(token: str | None) -> str | None:
    if token is None:
        return None
    return _fernet().decrypt(token.encode()).decode()

def hash_passphrase(passphrase: str) -> str:
    # bcrypt, con coste razonable
    return bcrypt.using(rounds=12).hash(passphrase)

def verify_passphrase(passphrase: str, hashed: str) -> bool:
    return bcrypt.verify(passphrase, hashed)
