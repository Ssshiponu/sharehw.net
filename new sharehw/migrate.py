from app import create_app, db
from models import User, Homework, AdminStudentApproval
from datetime import datetime

def migrate_database():
    app = create_app()
    with app.app_context():
        # Add created_at column to user table
        db.engine.execute('ALTER TABLE user ADD COLUMN created_at DATETIME')
        db.engine.execute('UPDATE user SET created_at = ? WHERE created_at IS NULL', (datetime.utcnow(),))
        
        # Add created_at column to homework table if it doesn't exist
        db.engine.execute('ALTER TABLE homework ADD COLUMN created_at DATETIME')
        db.engine.execute('UPDATE homework SET created_at = ? WHERE created_at IS NULL', (datetime.utcnow(),))
        
        # Add created_at and updated_at columns to admin_student_approval table
        db.engine.execute('ALTER TABLE admin_student_approval ADD COLUMN created_at DATETIME')
        db.engine.execute('ALTER TABLE admin_student_approval ADD COLUMN updated_at DATETIME')
        db.engine.execute('UPDATE admin_student_approval SET created_at = ? WHERE created_at IS NULL', (datetime.utcnow(),))
        
        print("Migration completed successfully!")

if __name__ == '__main__':
    migrate_database()
