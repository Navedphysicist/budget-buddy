from pydantic import BaseModel
from datetime import date
from typing import Optional

class IncomeBase(BaseModel):
    amount: float
    date: date
    source: str
    is_recurring: bool = False

class IncomeCreate(IncomeBase):
    pass

class IncomeUpdate(BaseModel):
    amount: Optional[float] = None
    source: Optional[str] = None
    date: date
    is_recurring: Optional[bool] = None

class Income(IncomeBase):
    id: int
    
    class Config:
        from_attributes = True
