from pydantic import BaseModel
from datetime import date
from typing import Optional
from schemas.category import CategoryBase
from schemas.payment_mode import PaymentModeBase


class ExpenseBase(BaseModel):
    amount: int
    date: date
    note: str
    recurring: bool = False
    category: Optional[CategoryBase] = None
    paymentMode: Optional[PaymentModeBase] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: Optional[str] = None
    date: date
    note: Optional[str] = None
    recurring: Optional[bool] = None
    category: Optional[CategoryBase] = None
    paymentMode: Optional[PaymentModeBase] = None


class Expense(ExpenseBase):
    id: int

    class Config:
        from_attributes = True
