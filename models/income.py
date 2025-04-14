from sqlalchemy import Column, Integer, Float, Boolean, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base


class DbIncome(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    source = Column(String, nullable=False)
    is_recurring = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("DbUser", back_populates="incomes")
