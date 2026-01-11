from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import sql
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timezone
from ..models import User
from ..database import get_db
from .. import utils, oauth2

router = APIRouter(prefix="/login", tags=["Authentication"])

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    cooldown = utils.user_cooldown(user_credentials.username, db)
    if cooldown is not None:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Please try again in {cooldown - datetime.now(timezone.utc)}")
    passwordHash = db.scalars(sql.select(User.password).where(User.email == user_credentials.username)).first()
    if not passwordHash or not utils.verify_pw(user_credentials.password, passwordHash):
        cd = utils.log_attempt(user_credentials.username, db)
        if cd is not None:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Please try again in {cd - datetime.now(timezone.utc)}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials, please try again.")
    utils.reset_attempts(user_credentials.username, db)
    access_token = oauth2.create_access_token(data={"user_id": user_credentials.username})
    return {'access_token' : access_token, 'token_type': "bearer"}
    
