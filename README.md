# Budget-Buddy Backend API

A FastAPI-based backend for the Budget-Buddy application that helps users manage their expenses, income, and budgets.

## Tech Stack

- FastAPI
- SQLite with SQLAlchemy ORM
- Pydantic for data validation
- Async SQLite support
- Python 3.12+

## Project Structure

```
app/
├── config.py           # Configuration settings
├── main.py            # FastAPI application
├── db/
│   ├── database.py    # Database configuration
│   └── seed.py        # Seed data
├── models/
│   └── models.py      # SQLAlchemy models
├── schemas/
│   └── schemas.py     # Pydantic schemas
└── routers/
    ├── testimonials.py
    ├── categories.py
    ├── expenses.py
    └── incomes.py
```

## Setup

1. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Create `.env` file with the following content:
```env
DATABASE_URL=sqlite+aiosqlite:///./budget_buddy.db
ENV=development
DEBUG=True
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

- Testimonials management
- Category management with budgets
- Expense tracking with filtering and CSV export
- Income management
- Payment modes tracking
- Budget vs Expense analysis