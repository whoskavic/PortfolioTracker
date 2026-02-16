from app.database import engine, Base
from app.models import User, Asset, Transaction, Position

def init_db():
    """
    Create all tables in the database
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Print all tables
    print("\nCreated tables:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    init_db()