from pydantic import BaseModel
from typing import Optional

class TestimonialBase(BaseModel):
    name: str
    role: str
    quote: str
    rating: int
    image: Optional[str] = None

class TestimonialCreate(TestimonialBase):
    pass

class Testimonial(TestimonialBase):
    id: int
    
    class Config:
        from_attributes = True
