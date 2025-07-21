#!/usr/bin/env python3
"""
Production startup script for the Expense Tracker API.
This script runs database migrations and starts the FastAPI server.
"""

import os
import sys
from pathlib import Path

import uvicorn
from sqlalchemy import create_engine, text

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

try:
    from alembic.config import Config
    from alembic import command
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False

from app.init_db import init_database


def check_database_state(engine):
    """Check the current state of the database."""
    try:
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            ))
            existing_tables = [row[0] for row in result.fetchall()]
            
            # Check if payment_method column exists in expenses table
            payment_method_exists = False
            if 'expenses' in existing_tables:
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'expenses' AND column_name = 'payment_method'"
                ))
                payment_method_exists = bool(result.fetchone())
            
            return {
                'tables_exist': bool(existing_tables),
                'existing_tables': existing_tables,
                'payment_method_exists': payment_method_exists
            }
    except Exception as e:
        print(f"❌ Error checking database state: {e}")
        return None


def run_alembic_migration(config, engine):
    """Run Alembic migration with proper error handling."""
    try:
        print("🔄 Running Alembic migration...")
        command.upgrade(config, "head")
        print("✅ Alembic migration completed successfully!")
        return True
    except Exception as e:
        print(f"⚠️  Alembic migration failed: {e}")
        return False


def run_sql_migration(engine):
    """Run SQL migration to add missing columns."""
    try:
        print("🔧 Running SQL migration...")
        
        with engine.connect() as conn:
            # Create PaymentMethod enum
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE paymentmethod AS ENUM (
                        'CREDIT_CARD', 'DEBIT_CARD', 'BANK_TRANSFER', 'CASH'
                    );
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            
            # Add missing columns
            conn.execute(text("""
                ALTER TABLE expenses 
                ADD COLUMN IF NOT EXISTS payment_method paymentmethod NOT NULL DEFAULT 'DEBIT_CARD'
            """))
            
            conn.execute(text("""
                ALTER TABLE expenses 
                ADD COLUMN IF NOT EXISTS billing_date TIMESTAMP WITH TIME ZONE
            """))
            
            conn.execute(text("""
                ALTER TABLE expenses 
                ADD COLUMN IF NOT EXISTS card_last_four VARCHAR(4)
            """))
            
            # Set billing_date for existing records
            conn.execute(text("""
                UPDATE expenses 
                SET billing_date = transaction_date 
                WHERE billing_date IS NULL
            """))
            
            conn.commit()
            print("✅ SQL migration completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ SQL migration failed: {e}")
        return False


def setup_database():
    """Set up the database with proper migration handling."""
    print("📦 Setting up database...")
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Handle Render's postgres URL format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print(f"🔗 Database URL: {database_url[:30]}...")
    
    # Create engine
    engine = create_engine(database_url)
    
    # Check database state
    db_state = check_database_state(engine)
    if db_state is None:
        print("❌ Cannot connect to database")
        sys.exit(1)
    
    print(f"📊 Database state: {db_state}")
    
    # Handle different scenarios
    if not db_state['tables_exist']:
        # Fresh database - create all tables
        print("🆕 Fresh database detected - creating tables...")
        init_database()
        print("✅ Database initialized successfully!")
        
    elif not db_state['payment_method_exists']:
        # Existing database needs migration
        print("📊 Existing database needs migration...")
        
        # Try Alembic first
        if ALEMBIC_AVAILABLE:
            alembic_cfg_path = Path(__file__).parent / "app" / "alembic.ini"
            if alembic_cfg_path.exists():
                config = Config(str(alembic_cfg_path))
                config.set_main_option("sqlalchemy.url", database_url)
                
                if run_alembic_migration(config, engine):
                    print("✅ Migration completed with Alembic!")
                else:
                    print("🔄 Alembic failed, trying SQL migration...")
                    if not run_sql_migration(engine):
                        print("❌ All migration methods failed")
                        sys.exit(1)
            else:
                print("❌ Alembic config not found, using SQL migration...")
                if not run_sql_migration(engine):
                    print("❌ SQL migration failed")
                    sys.exit(1)
        else:
            print("📋 Alembic not available, using SQL migration...")
            if not run_sql_migration(engine):
                print("❌ SQL migration failed")
                sys.exit(1)
    else:
        # Database is up to date
        print("✅ Database is up to date!")


def main():
    """Main startup function."""
    print("🚀 Starting Expense Tracker API...")
    
    # Set up database
    setup_database()
    print("✅ Database ready!")
    
    # Start the server
    print("🌐 Starting FastAPI server...")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT") != "production"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        access_log=True
    )


if __name__ == "__main__":
    main()
