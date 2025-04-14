from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import get_db
from models.category import DbCategory
from models.expense import DbExpense
from schemas.category import Category as CategorySchema, CategoryWithExpense
from typing import List

router = APIRouter()

@router.get("/categories", response_model=List[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(DbCategory).all()
    return categories

@router.get("/category_expense", response_model=List[CategoryWithExpense])
def get_category_expenses(db: Session = Depends(get_db)):
    query = db.query(
        DbCategory,
        func.coalesce(func.sum(DbExpense.amount), 0).label('expense')
    ).outerjoin(DbExpense).group_by(DbCategory.id)
    
    result = query.all()
    categories = []
    for row in result:
        category_dict = row[0].__dict__
        category_dict['expense'] = float(row[1])
        categories.append(category_dict)
    return categories

@router.get("/category_budget", response_model=List[CategorySchema])
def get_category_budgets(db: Session = Depends(get_db)):
    categories = db.query(DbCategory).all()
    return categories
