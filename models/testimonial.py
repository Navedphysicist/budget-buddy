from sqlalchemy import Column, Integer, String
from db.database import Base

class DbTestimonial(Base):
    __tablename__ = "testimonials"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    quote = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    image = Column(String, nullable=True)
