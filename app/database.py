import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Only load .env in development
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

# Database configuration with better defaults for Render
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Development fallback
    DATABASE_URL = "postgresql://user:password@localhost:5432/expense_tracker"

# Handle Render's postgres URL format (postgres:// vs postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
