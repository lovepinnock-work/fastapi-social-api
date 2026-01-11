from pwdlib import PasswordHash
from sqlalchemy import delete, update, insert
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from .config import settings
from .models import Attempts

password_hasher = PasswordHash.recommended()

def hash(password: str) -> str:
    return password_hasher.hash(password)

def verify_pw(plain_pw: str, hashed_pw: str) -> bool:
    return password_hasher.verify(plain_pw, hashed_pw)

def user_cooldown(user_id: str, db: Session) -> datetime | None: # Check if user cooldown active, reset if expired
    now = datetime.now(timezone.utc)
    row = db.get(Attempts, user_id)

    if not row:
        return None

    if row.cooldown is not None:
        if now >= row.cooldown:
            db.execute(delete(Attempts).where(Attempts.user_id == user_id))
            db.commit()
            return None
        return row.cooldown

    return None


def log_attempt(user_id: str, db: Session) -> datetime | None: # Log user attempt and set cooldown if max login attempts reached
    now = datetime.now(timezone.utc)
    row = db.get(Attempts, user_id)

    if row is None:
        db.execute(insert(Attempts).values(user_id=user_id, attempts=1, cooldown=None))
        db.commit()
        return None

    new_attempts = row.attempts + 1

    if new_attempts > settings.max_login_attempts:
        cd = now + timedelta(minutes=settings.login_attempt_cooldown_window)
        db.execute(
            update(Attempts)
            .where(Attempts.user_id == user_id)
            .values(attempts=new_attempts, cooldown=cd)
        )
        db.commit()
        return cd

    db.execute(
        update(Attempts)
        .where(Attempts.user_id == user_id)
        .values(attempts=new_attempts)
    )
    db.commit()
    return None


def reset_attempts(user_id: str, db: Session) -> None: # Delete user attempt entry, resetting attempts back to zero
    db.execute(delete(Attempts).where(Attempts.user_id == user_id))
    db.commit()

    