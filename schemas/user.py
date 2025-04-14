from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    phone_number: str = Field(pattern=r'^\+\d{12}$')


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserVerify(BaseModel):
    phone_number: str = Field(pattern=r'^\+\d{12}$')
    verification_code: str = Field(min_length=6, max_length=6)

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True