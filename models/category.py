from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from db.database import Base

class DbCategory(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    budget = Column(Float, nullable=False)
    color = Column(String, nullable=True)
    expenses = relationship("DbExpense", back_populates="category")


