from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.database import Base

class DbPaymentMode(Base):
    __tablename__ = "payment_modes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=False)
    color = Column(String, nullable=True)
    expenses = relationship("DbExpense", back_populates="paymentMode")
