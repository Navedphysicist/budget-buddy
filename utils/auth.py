from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from models.user import DbUser
from utils.token import verify_token, TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> DbUser:
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception

    user = db.query(DbUser).filter(
        DbUser.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your account first",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
