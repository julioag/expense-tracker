"""
Database initialization script.
This script creates the database tables and populates them with default data.
"""

from database import Base, SessionLocal, engine
from models import Category
from sqlalchemy.orm import Session


def create_default_categories(db: Session):
    """Create default expense categories."""
    default_categories = [
        {
            "name": "Food & Dining",
            "description": "Restaurants, groceries, food delivery",
            "color": "#FF6B6B",
        },
        {
            "name": "Transportation",
            "description": "Gas, public transport, ride sharing, car maintenance",
            "color": "#4ECDC4",
        },
        {
            "name": "Shopping",
            "description": "Clothing, electronics, general purchases",
            "color": "#45B7D1",
        },
        {
            "name": "Bills & Utilities",
            "description": "Electricity, water, internet, phone, rent",
            "color": "#FFA07A",
        },
        {
            "name": "Entertainment",
            "description": "Movies, streaming, games, hobbies",
            "color": "#98D8C8",
        },
        {
            "name": "Healthcare",
            "description": "Medical, dental, pharmacy, insurance",
            "color": "#F7DC6F",
        },
        {
            "name": "Education",
            "description": "Courses, books, training, subscriptions",
            "color": "#BB8FCE",
        },
        {
            "name": "Travel",
            "description": "Flights, hotels, vacation expenses",
            "color": "#85C1E9",
        },
        {"name": "Other", "description": "Miscellaneous expenses", "color": "#D5DBDB"},
    ]

    for cat_data in default_categories:
        # Check if category already exists
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()

        if not existing:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"],
                color=cat_data["color"],
            )
            db.add(category)

    db.commit()
    print(f"Created {len(default_categories)} default categories")


def init_database():
    """Initialize the database with tables and default data."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    print("Adding default categories...")
    db = SessionLocal()
    try:
        create_default_categories(db)
        print("Database initialization completed successfully!")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
