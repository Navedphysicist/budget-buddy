from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.database import get_db
from models.user import DbUser
from schemas.user import UserCreate, UserVerify
from utils.twilio_service import TwilioService
from utils.security import get_password_hash, verify_password
from utils.token import create_access_token
from typing import Dict

router = APIRouter(
    prefix="/users",
    tags=["users"]
)
twilio_service = TwilioService()


@router.post("/signup", response_model=Dict[str, str])
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    if db.query(DbUser).filter(DbUser.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if db.query(DbUser).filter(DbUser.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    if db.query(DbUser).filter(DbUser.phone_number == user.phone_number).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    # Generate verification code
    verification_code = twilio_service.generate_verification_code()

    # Create new user
    db_user = DbUser(
        email=user.email,
        username=user.username,
        phone_number=user.phone_number,
        hashed_password=get_password_hash(user.password),
        verification_code=verification_code
    )

    # Send verification code
    success,message = twilio_service.send_verification_code(
        user.phone_number, verification_code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code"
        )

    db.add(db_user)
    db.commit()

    return {"message": "Verification code sent to your phone number"}


@router.post("/verify", response_model=Dict[str, str])
def verify_user(verification: UserVerify, db: Session = Depends(get_db)):
    user = db.query(DbUser).filter(DbUser.phone_number ==
                                   verification.phone_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.verification_code != verification.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

    user.is_verified = True
    user.verification_code = None
    db.commit()

    # Generate access token with username
    access_token = create_access_token(data={"sub": user.username})

    return {
        "message": "User verified successfully",
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=Dict[str, str])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DbUser).filter(DbUser.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username"
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect  password"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your account first"
        )

    # Generate access token with username
    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
