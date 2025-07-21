#!/usr/bin/env python3
"""
Production startup script for the Expense Tracker API.
This script runs database migrations and starts the FastAPI server.
"""

import os
from pathlib import Path
import sys

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


def run_migrations():
    """Run Alembic migrations if available, otherwise initialize database."""
    print("📦 Checking database state...")
    
    try:
        if not ALEMBIC_AVAILABLE:
            print("📋 Alembic not available - using direct table creation...")
            init_database()
            return
        
        # Check if we have an Alembic configuration
        alembic_cfg_path = Path(__file__).parent / "app" / "alembic.ini"
        print(f"🔍 Looking for Alembic config at: {alembic_cfg_path}")
        
        if alembic_cfg_path.exists():
            print("✅ Found Alembic config file")
            print("🔄 Running Alembic migrations...")
            
            # Configure Alembic
            config = Config(str(alembic_cfg_path))
            
            # Set the database URL from environment
            database_url = os.getenv("DATABASE_URL")
            print(f"🔗 Database URL: {database_url[:20]}..." if database_url else "❌ No DATABASE_URL found")
            
            if database_url:
                config.set_main_option("sqlalchemy.url", database_url)
            
            # Check if we have any tables (to distinguish fresh vs existing DB)
            db_url = database_url or config.get_main_option("sqlalchemy.url")
            print(f"🔗 Using DB URL: {db_url[:30]}...")
            
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public'"
                ))
                existing_tables = [row[0] for row in result.fetchall()]
                print(f"📊 Found existing tables: {existing_tables}")
            
            if not existing_tables:
                # Fresh database - create all tables from models
                print("🆕 Fresh database detected - creating tables from models...")
                init_database()
            else:
                # Existing database - run migrations
                print("📊 Existing database detected - applying migrations...")
                try:
                    print("🚀 Running: alembic upgrade head")
                    command.upgrade(config, "head")
                    print("✅ Migrations completed successfully!")
                    
                    # Verify the migration worked
                    with engine.connect() as conn:
                        result = conn.execute(text(
                            "SELECT column_name FROM information_schema.columns "
                            "WHERE table_name = 'expenses' AND column_name = 'payment_method'"
                        ))
                        if result.fetchone():
                            print("✅ payment_method column exists!")
                        else:
                            print("❌ payment_method column still missing!")
                            
                except Exception as migration_error:
                    print(f"⚠️  Migration error: {migration_error}")
                    print("🔄 Falling back to table creation...")
                    init_database()
        else:
            # No Alembic config - use direct table creation
            print(f"❌ No Alembic config found at {alembic_cfg_path}")
            print("📋 Using direct table creation...")
            init_database()
            
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        print("🔄 Attempting direct table creation...")
        try:
            init_database()
        except Exception as init_error:
            print(f"❌ Database initialization failed: {init_error}")
            sys.exit(1)


def main():
    """Main startup function."""
    print("🚀 Starting Expense Tracker API...")

    # Run migrations or initialize database
    run_migrations()
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
