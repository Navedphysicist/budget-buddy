from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, Date, String
from sqlalchemy.orm import relationship
from db.database import Base


class DbExpense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    note = Column(String, nullable=True)
    recurring = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    payment_mode_id = Column(Integer, ForeignKey("payment_modes.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    category = relationship("DbCategory", back_populates="expenses")
    paymentMode = relationship("DbPaymentMode", back_populates="expenses")
    user = relationship("DbUser", back_populates="expenses")