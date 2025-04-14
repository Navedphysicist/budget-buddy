from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from db.database import get_db
from models.income import DbIncome
from models.user import DbUser
from schemas.income import Income as IncomeSchema, IncomeCreate, IncomeUpdate
from typing import List, Optional
from datetime import datetime
from utils.auth import get_current_user

router = APIRouter()


@router.get("/income", response_model=List[IncomeSchema])
def get_incomes(
    recurring: Optional[bool] = None,
    source: Optional[str] = None,
    month: Optional[str] = None,
    top: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    query = db.query(DbIncome).filter(DbIncome.user_id == current_user.id)

    if recurring is not None:
        query = query.filter(DbIncome.is_recurring == recurring)
    if source:
        query = query.filter(DbIncome.source == source)
    if month:
        try:
            date = datetime.strptime(month, '%Y-%m')
            query = query.filter(
                extract('year', DbIncome.date) == date.year,
                extract('month', DbIncome.date) == date.month
            )
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid month format. Use YYYY-MM")

    query = query.order_by(DbIncome.date.desc())

    if top:
        query = query.limit(top)

    return query.all()


@router.post("/income", response_model=IncomeSchema, status_code=201)
def create_income(
    income: IncomeCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    db_income = DbIncome(**income.model_dump(), user_id=current_user.id)
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income


@router.get("/income/{income_id}", response_model=IncomeSchema)
def get_income(
    income_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    income = db.query(DbIncome).filter(
        DbIncome.id == income_id,
        DbIncome.user_id == current_user.id
    ).first()
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    return income


@router.put("/income/{income_id}", response_model=IncomeSchema)
def update_income(
    income_id: int,
    income: IncomeUpdate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    db_income = db.query(DbIncome).filter(
        DbIncome.id == income_id,
        DbIncome.user_id == current_user.id
    ).first()
    if not db_income:
        raise HTTPException(status_code=404, detail="Income not found")

    update_data = income.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_income, field, value)

    db.commit()
    db.refresh(db_income)
    return db_income


@router.delete("/income/{income_id}")
def delete_income(
    income_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    income = db.query(DbIncome).filter(
        DbIncome.id == income_id,
        DbIncome.user_id == current_user.id
    ).first()
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")

    db.delete(income)
    db.commit()
    return {"message": "Income deleted successfully"}
