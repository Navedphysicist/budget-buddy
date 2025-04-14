from pydantic import BaseModel
from typing import Optional

class PaymentModeBase(BaseModel):
    name: str
    icon: str
    color: Optional[str] = None

class PaymentModeCreate(PaymentModeBase):
    pass

class PaymentMode(PaymentModeBase):
    id: int
    
    class Config:
        from_attributes = True
