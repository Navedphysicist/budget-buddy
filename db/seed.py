from sqlalchemy.orm import Session
from models.testimonial import DbTestimonial
from models.category import DbCategory
from models.payment_mode import DbPaymentMode


def seed_data(db: Session):
    # Seed testimonials
    testimonials = [
        DbTestimonial(
            name="Richard James",
            role="Small Business Owner",
            quote="BudgetBuddy has transformed how I manage my business finances. The intuitive interface and powerful tracking tools have saved me countless hours.",
            rating=5,
            image="https://mighty.tools/mockmind-api/content/human/1.jpg"
        ),
        DbTestimonial(
            name="Sarah White",
            role="Freelance Consultant",
            quote="As a professional, I need reliable financial tools. BudgetBuddy delivers with its comprehensive reporting and budget management features.",
            rating=5,
            image="https://mighty.tools/mockmind-api/content/human/2.jpg"
        ),
        DbTestimonial(
            name="Emma Brown",
            role="Entrepreneur",
            quote="The receipt scanner feature has been a game-changer for tracking my expenses. I highly recommend BudgetBuddy to anyone looking to improve their financial management.",
            rating=4,
            image="https://mighty.tools/mockmind-api/content/human/3.jpg"
        )
    ]

    # Seed categories
    categories = [
        DbCategory(name="Food expenses", icon="Utensils",
                   budget=5000, color="amber"),
        DbCategory(name="Shopping", icon="ShoppingCart",
                   budget=8000, color="blue"),
        DbCategory(name="Entertainment", icon="Gamepad",
                   budget=3000, color="purple"),
        DbCategory(name="Medical", icon="Stethoscope",
                   budget=2000, color="red"),
        DbCategory(name="Bills and Utilities",
                   icon="FileText", budget=4000, color="gray"),
        DbCategory(name="Education", icon="GraduationCap",
                   budget=7000, color="green")
    ]

    # Seed payment modes
    payment_modes = [
        DbPaymentMode(name="Cash", icon="Wallet", color="green"),
        DbPaymentMode(name="Credit Card", icon="CreditCard", color="blue"),
        DbPaymentMode(name="Debit Card", icon="Card", color="purple"),
        DbPaymentMode(name="UPI", icon="QrCode", color="orange"),
        DbPaymentMode(name="Net Banking", icon="Bank", color="gray")
    ]

    # Add all to session
    for testimonial in testimonials:
        db.add(testimonial)

    for category in categories:
        db.add(category)

    for payment_mode in payment_modes:
        db.add(payment_mode)

    # Commit the session
    db.commit()


if __name__ == "__main__":
    from db.database import SessionLocal
    db = SessionLocal()
    seed_data(db)
    print("Database seeded successfully!")
