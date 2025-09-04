# api/security.py
from datetime import datetime, timezone
import os
from typing import Dict, Any, Iterable

from cryptography.fernet import Fernet
from passlib.context import CryptContext
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

# ---- HASH de contraseñas (bcrypt) ----
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_passphrase(passphrase: str) -> str:
    if not passphrase:
        raise ValueError("passphrase is required")
    return _pwd_ctx.hash(passphrase)

def verify_passphrase(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)

# ---- CIFRADO de datos personales (Fernet/AES) ----
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY is not set in .env")

_fernet = Fernet(FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY)

PERSONAL_FIELDS: Iterable[str] = (
    "full_name", "name",
    "address",
    "dob", "date_of_birth",
    "phone", "phone_number",
    "disabilities",
)

def _enc_str(s: str) -> str:
    return _fernet.encrypt(str(s).encode()).decode()

def _dec_str(t: str) -> str:
    return _fernet.decrypt(str(t).encode()).decode()

def encrypt_personal(data: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(data)
    for k in PERSONAL_FIELDS:
        if k in out and out[k] is not None:
            v = out[k]
            out[k] = [_enc_str(x) for x in v] if isinstance(v, list) else _enc_str(v)
    return out

def decrypt_personal(data: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(data)
    for k in PERSONAL_FIELDS:
        if k in out and out[k] is not None:
            v = out[k]
            try:
                out[k] = [_dec_str(x) for x in v] if isinstance(v, list) else _dec_str(v)
            except Exception:
                pass  # si ya está en claro o no es token válido, lo dejamos
    return out

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
