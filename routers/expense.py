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
import io
from utils.auth import get_current_user

router = APIRouter()


@router.get("/expense", response_model=List[ExpenseSchema])
def get_expenses(
    category: Optional[str] = None,
    recurring: Optional[bool] = None,
    month: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, gt=0),
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user)
):
    query = db.query(DbExpense).filter(DbExpense.user_id == current_user.id)

    # Apply filters
    if category:
        query = query.filter(DbExpense.category.has(name=category))
    if recurring is not None:
        query = query.filter(DbExpense.recurring == recurring)
    if month:
        try:
            date = datetime.strptime(month, '%Y-%m')
            query = query.filter(
                extract('year', DbExpense.date) == date.year,
                extract('month', DbExpense.date) == date.month
            )
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid month format. Use YYYY-MM")
    if search:
        query = query.filter(DbExpense.note.like(f"%{search}%"))

    # Add sorting
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

    # Then, find or create the payment mode
    payment_mode = db.query(DbPaymentMode).filter(
        DbPaymentMode.name == expense.paymentMode.name,
        DbPaymentMode.icon == expense.paymentMode.icon,
        DbPaymentMode.color == expense.paymentMode.color
    ).first()

    if not payment_mode:
        payment_mode = DbPaymentMode(**expense.paymentMode.model_dump())
        db.add(payment_mode)
        db.flush()

    # Create the expense with the found/created category and payment mode
    expense_data = expense.model_dump(exclude={'category', 'paymentMode'})
    db_expense = DbExpense(
        **expense_data,
        category_id=category.id,
        payment_mode_id=payment_mode.id,
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
        payment_mode = db.query(DbPaymentMode).filter(
            DbPaymentMode.name == payment_data['name'],
            DbPaymentMode.icon == payment_data['icon'],
            DbPaymentMode.color == payment_data.get('color')
        ).first()

        if not payment_mode:
            payment_mode = DbPaymentMode(**payment_data)
            db.add(payment_mode)
            db.flush()

        expense.payment_mode_id = payment_mode.id

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
        'payment_mode': expense.payment_mode.name if expense.payment_mode else None
    } for expense in expenses]

    # Create CSV
    df = pd.DataFrame(expense_data)
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    response = StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=expenses_{datetime.now().strftime('%Y%m%d')}.csv"}
    )
    return response
