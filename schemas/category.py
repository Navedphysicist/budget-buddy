from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    icon: str
    color: str
    budget: float = 0  


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class CategoryWithExpense(Category):
    expense: float
