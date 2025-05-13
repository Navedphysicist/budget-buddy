from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from db.database import get_db
from models.expense import DbExpense
from models.category import DbCategory
from models.payment_mode import DbPaymentMode
from models.user import DbUser
from schemas.expense import Expense as ExpenseSchema, ExpenseCreate, ExpenseUpdate
from typing import List, Optional
from datetime import datetime
import pandas as pd
from fastapi.responses import StreamingResponse
from utils.auth import get_current_user
from calendar import monthrange

router = APIRouter()


@router.get("/expense", response_model=List[ExpenseSchema])
def get_expenses(
    category: Optional[str] = Query(None, min_length=1, description="Category name (case-sensitive partial match)"),
    recurring: Optional[bool] = Query(None, description="Filter by recurring status: true or false"),
    month: Optional[str] = Query(None, regex=r"^\d{4}-(0[1-9]|1[0-2])$", description="Month in YYYY-MM format"),
    search: Optional[str] = Query(None, min_length=1, description="Search expense notes (case-insensitive, partial match)"),
    page: int = Query(1, gt=0, description="Pagination: page number (starting from 1)"),
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    query = db.query(DbExpense).filter(DbExpense.user_id == current_user.id)

    # Apply filters
    if category and category.strip():
       query = query.filter(DbExpense.category.has(DbCategory.name.ilike(f"%{category.strip()}%")))

    if recurring is not None:
        query = query.filter(DbExpense.recurring == recurring)

    if month:
        date = datetime.strptime(month, '%Y-%m')
        start_date = date.replace(day=1)
        last_day = monthrange(date.year, date.month)[1]
        end_date = date.replace(day=last_day)
        query = query.filter(DbExpense.date.between(start_date, end_date))

    if search and search.strip():
        query = query.filter(DbExpense.note.ilike(f"%{search.strip()}%"))

    # Sort by most recent date
    query = query.order_by(DbExpense.date.desc())

    # Pagination
    limit = 10
    offset = (page - 1) * limit
    expenses = query.offset(offset).limit(limit).all()

    return expenses


@router.post("/expense", response_model=ExpenseSchema, status_code=201)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    # First, find or create the category
    category = db.query(DbCategory).filter(
        DbCategory.name == expense.category.name,
        DbCategory.icon == expense.category.icon,
        DbCategory.color == expense.category.color
    ).first()

    if not category:
        category = DbCategory(
            name=expense.category.name,
            icon=expense.category.icon,
            color=expense.category.color,
            budget=expense.category.budget  # Include budget
        )
        db.add(category)
        db.flush()

    print(expense,"PaymentMode")

    paymentMode = db.query(DbPaymentMode).filter(
        DbPaymentMode.name == expense.paymentMode.name,
        DbPaymentMode.icon == expense.paymentMode.icon,
        DbPaymentMode.color == expense.paymentMode.color
    ).first()

    if not paymentMode:
        paymentMode = DbPaymentMode(**expense.paymentMode.model_dump())
        db.add(paymentMode)
        db.flush()

    # Create the expense with the found/created category and payment mode
    expense_data = expense.model_dump(exclude={'category', 'paymentMode'})
    db_expense = DbExpense(
        **expense_data,
        category_id=category.id,
        payment_mode_id=paymentMode.id,
        user_id=current_user.id
    )

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.delete("/expense/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    expense = db.query(DbExpense).filter(
        DbExpense.id == expense_id,
        DbExpense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted"}


@router.patch("/expense/{expense_id}", response_model=ExpenseSchema)
def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    expense = db.query(DbExpense).filter(
        DbExpense.id == expense_id,
        DbExpense.user_id == current_user.id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data = expense_update.model_dump(exclude_unset=True)

    # Handle category update if provided
    if 'category' in update_data:
        category_data = update_data.pop('category')
        category = db.query(DbCategory).filter(
            DbCategory.name == category_data['name'],
            DbCategory.icon == category_data['icon'],
            DbCategory.color == category_data.get('color')
        ).first()

        if not category:
            category = DbCategory(**category_data)
            db.add(category)
            db.flush()

        expense.category_id = category.id

    # Handle payment mode update if provided
    if 'paymentMode' in update_data:
        payment_data = update_data.pop('paymentMode')
        paymentMode = db.query(DbPaymentMode).filter(
            DbPaymentMode.name == payment_data['name'],
            DbPaymentMode.icon == payment_data['icon'],
            DbPaymentMode.color == payment_data.get('color')
        ).first()

        if not paymentMode:
            paymentMode = DbPaymentMode(**payment_data)
            db.add(paymentMode)
            db.flush()

        expense.paymentMode_id = paymentMode.id

    # Update other fields
    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.get("/getCSV")
def get_expenses_csv(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    expenses = db.query(DbExpense).filter(
        DbExpense.user_id == current_user.id
    ).order_by(DbExpense.date.desc()).all()

    # Convert to DataFrame
    expense_data = [{
        'id': expense.id,
        'amount': expense.amount,
        'date': expense.date,
        'note': expense.note,
        'recurring': expense.recurring,
        'category': expense.category.name if expense.category else None,
        'paymentMode': expense.paymentMode.name if expense.paymentMode else None
    } for expense in expenses]

    # Create CSV
    def iter_csv():
        df = pd.DataFrame(expense_data)
        yield df.to_csv(index=False)

    return StreamingResponse(
        iter_csv(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=expenses_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )
