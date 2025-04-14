from app.db.database import engine, Base, SessionLocal
from app.db.seed import seed_data

def main():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session and seed the data
    db = SessionLocal()
    try:
        seed_data(db)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    main()
