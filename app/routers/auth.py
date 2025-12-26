from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import sql
from sqlalchemy.orm import Session
from typing import Annotated
from ..models import User
from ..schemas import UserLogin
from ..database import get_db
from .. import utils, oauth2

router = APIRouter(prefix="/login", tags=["Authentication"])
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    result = db.scalars(sql.select(User.password).where(User.email == user_credentials.username))
    passwordHash = result.first()
    if not passwordHash:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No account found matching those credenitals")
    if not utils.verify_pw(user_credentials.password, passwordHash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials, please try again.")
    access_token = oauth2.create_access_token(data={"user_id": user_credentials.username})
    return {'access_token' : access_token, 'token_type': "bearer"}
    
