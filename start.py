#!/usr/bin/env python3
"""
Production startup script for the Expense Tracker API.
This script initializes the database and starts the FastAPI server.
"""

import os
from pathlib import Path
import sys

import uvicorn

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.init_db import init_database


def main():
    """Main startup function."""
    print("🚀 Starting Expense Tracker API...")

    # Initialize database
    print("📦 Initializing database...")
    try:
        init_database()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

    # Start the server
    print("🌐 Starting FastAPI server...")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENVIRONMENT") != "production"

    uvicorn.run("app.main:app", host=host, port=port, reload=reload, access_log=True)


if __name__ == "__main__":
    main()
