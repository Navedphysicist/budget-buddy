import json
from pathlib import Path
from sqlalchemy.orm import Session
from models.testimonial import DbTestimonial
from models.category import DbCategory
from models.payment_mode import DbPaymentMode


def load_data_from_json():

    filename="data.json"
    # Get the path to the current seed.py file
    base_dir = Path(__file__).parent

    # Build full path to the data.json file inside the same folder
    file_path = base_dir / filename

    # Open and load the JSON file
    with open(file_path, "r") as file:
        return json.load(file)


def seed_data(db: Session, data: dict):
    # Seed testimonials
    for item in data.get("testimonials", []):
        testimonial = DbTestimonial(**item)
        db.add(testimonial)

    # Seed categories
    for item in data.get("categories", []):
        category = DbCategory(**item)
        db.add(category)

    # Seed payment modes
    for item in data.get("payment_modes", []):
        payment_mode = DbPaymentMode(**item)
        db.add(payment_mode)

    db.commit()


if __name__ == "__main__":
    from db.database import SessionLocal

    db = SessionLocal()
    data = load_data_from_json()
    seed_data(db, data)
    print("Database seeded successfully!")
