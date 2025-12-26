from pwdlib import PasswordHash
from typing import Optional
import jwt
import subprocess
from datetime import datetime, timezone, timedelta

password_hasher = PasswordHash.recommended()

def hash(password: str) -> str:
    return password_hasher.hash(password)

def verify_pw(plain_pw: str, hashed_pw: str) -> bool:
    return password_hasher.verify(plain_pw, hashed_pw)