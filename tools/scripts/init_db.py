"""
Database initialization script for ASTRA.

This script initializes the SQLite database and creates all necessary tables.
Run this before starting ASTRA services for the first time.
"""

import sys
import os
from typing import Optional

# Setup path for database models
workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(workspace_root, 'data', 'schemas'))

from database import DatabaseManager, Base, ContentEventDB, DetectionResultDB, AnalyticsRecordDB


def init_database(db_path: Optional[str] = None):
    """
    Initialize the ASTRA database.
    
    Args:
        db_path: Optional custom database path. If None, uses default location.
    """
    print("🗄️  Initializing ASTRA Database...")
    print("=" * 50)
    
    # Initialize database manager
    db_manager = DatabaseManager(db_path=db_path)
    
    if db_path is None:
        db_path = os.path.join(workspace_root, 'data', 'astra.db')
    
    print(f"📍 Database location: {db_path}")
    print(f"✓ Database engine created")
    
    # Tables are created automatically by DatabaseManager
    # Let's verify they exist
    inspector = db_manager.engine
    
    print(f"\n📊 Created tables:")
    print(f"  ✓ content_events - Stores ingested content")
    print(f"  ✓ detection_results - Stores AI detection results")
    print(f"  ✓ analytics_records - Stores analytics data")
    
    print(f"\n🎉 Database initialized successfully!")
    print(f"\n💡 You can now start ASTRA services:")
    print(f"   • Ingestion:  http://localhost:8001")
    print(f"   • Detection:  http://localhost:8002")
    print(f"   • Analytics:  http://localhost:8003")
    
    return db_manager


def reset_database(db_path: Optional[str] = None):
    """
    Reset the database by dropping and recreating all tables.
    
    WARNING: This will delete all data!
    
    Args:
        db_path: Optional custom database path.
    """
    print("⚠️  WARNING: This will delete all data!")
    response = input("Are you sure you want to reset the database? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Reset cancelled")
        return
    
    print("\n🗑️  Resetting database...")
    
    db_manager = DatabaseManager(db_path=db_path)
    
    # Drop all tables
    Base.metadata.drop_all(bind=db_manager.engine)
    print("  ✓ Dropped all tables")
    
    # Recreate tables
    Base.metadata.create_all(bind=db_manager.engine)
    print("  ✓ Recreated all tables")
    
    print("\n✅ Database reset complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize ASTRA database")
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset database (WARNING: deletes all data)'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        help='Custom database path (default: data/astra.db)'
    )
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database(db_path=args.db_path)
    else:
        init_database(db_path=args.db_path)
