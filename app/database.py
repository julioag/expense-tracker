import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Only load .env in development
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

# Database configuration with better defaults for Render
# Check DATABASE_URL first (standard), then DATABASE_POSTGRES_URL (Vercel/Supabase integration)
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE_POSTGRES_URL")

if not DATABASE_URL:
    # Development fallback
    DATABASE_URL = "postgresql://user:password@localhost:5432/expense_tracker"

# Handle Render's postgres URL format (postgres:// vs postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Sanitize URL to remove invalid query parameters that might confuse psycopg2
# (e.g., "supa" or other malformed options from copy-paste errors)
try:
    from sqlalchemy.engine.url import make_url
    
    url_obj = make_url(DATABASE_URL)
    
    # List of known valid libpq parameters or driver arguments
    # We'll allow common ones and strip others if they look suspicious
    # For now, we'll just strip 'supa' if it exists, or rebuild without unknown params if needed.
    # But 'supa' as a key suggests it's in the query args.
    
    if url_obj.query:
        # Create a new query dict without keys that are likely invalid
        # The error 'invalid connection option "supa"' means 'supa' is a key.
        new_query = {k: v for k, v in url_obj.query.items() if k.lower() != 'supa'}
        
        # Also strip 'options' if it contains 'supa' and looks malformed?
        # But usually 'supa' appears as a key itself if the URL is like ?supa=...
        
        if len(new_query) != len(url_obj.query):
            print(f"⚠️ Removed invalid query parameters from DATABASE_URL: {set(url_obj.query) - set(new_query)}")
            url_obj = url_obj._replace(query=new_query)
            DATABASE_URL = str(url_obj)
    
    # Debug: Print the username being used (masked)
    print(f"🔌 Connecting to database as user: '{url_obj.username}' on host: '{url_obj.host}' port: '{url_obj.port}'")
            
except Exception as e:
    print(f"⚠️ Error sanitizing DATABASE_URL: {e}")

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
