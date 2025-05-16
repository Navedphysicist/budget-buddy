from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from models.user import DbUser
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from pydantic import BaseModel
from config import settings



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token:str = Depends(oauth2_scheme),db:Session = Depends(get_db)):

    credential_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])

        username = payload.get('sub')
        if username is None:
            raise  credential_exception
        
    except JWTError:
        raise  credential_exception
    
    user = db.query(DbUser).filter(DbUser.username == username).first()
    if user is None:
        raise  credential_exception
    return user