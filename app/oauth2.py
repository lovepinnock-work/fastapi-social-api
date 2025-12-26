import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .schemas import TokenData
from .database import get_db
from .models import User
from sqlalchemy.orm import Session
from sqlalchemy import select
from .config import settings

ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRATION_MINUTES = settings.access_token_expiration_minutes
SECRET_KEY = settings.secret_key

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

def create_access_token(data: dict, expires: int = ACCESS_TOKEN_EXPIRATION_MINUTES):
    copy_of_data = data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=expires)
    copy_of_data.update({"exp" : expiration})
    encoded_jwt = jwt.encode(payload=copy_of_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid Credentials",
        headers={"WWW-Authenticate" : "Bearer"})    
    try: 
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("user_id")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError as error:
        print("Error: ", error)
        raise credentials_exception
    return token_data

def get_current_active_user(token_data: Annotated[TokenData, Depends(verify_access_token)], 
                            db: Session = Depends(get_db)):
    if not token_data.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not Authenticated")
    res = db.scalar(select(User).where(User.email == token_data.email))
    return res