#!/usr/bin/env python3
"""Database migration script to add missing columns"""
from app import app
from sqlalchemy import text, inspect

def migrate_database():
    """Add missing columns to existing tables"""
    with app.app_context():
        from models import db
        
        inspector = inspect(db.engine)
        
        # Check if project_submissions table exists
        if 'project_submissions' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('project_submissions')]
            
            # Add submission_type column if it doesn't exist
            if 'submission_type' not in columns:
                print("Adding submission_type column to project_submissions table...")
                try:
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE project_submissions ADD COLUMN submission_type VARCHAR(50) DEFAULT 'project'"))
                        conn.commit()
                    print("✓ Successfully added submission_type column")
                except Exception as e:
                    print(f"✗ Error adding submission_type column: {e}")
            else:
                print("✓ submission_type column already exists")
        else:
            print("project_submissions table doesn't exist yet (will be created on next init)")
        
        # Ensure notifications table exists
        if 'notifications' not in inspector.get_table_names():
            print("Creating notifications table...")
            from models import Notification
            db.create_all()
            print("✓ Created notifications table")
        else:
            print("✓ notifications table already exists")
        
        print("\nMigration complete!")

if __name__ == '__main__':
    migrate_database()
