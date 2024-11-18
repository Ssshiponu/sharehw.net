from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(6), nullable=False)
    class_name = db.Column(db.String(3), nullable=False)  # XI or XII
    section = db.Column(db.String(20), nullable=False)  # Science-A, Science-B, Arts, Commerce
    role = db.Column(db.String(20), nullable=False)  # student, captain, admin-student, admin
    password_hash = db.Column(db.String(128))  # Only for captain and admin-student
    is_approved = db.Column(db.Boolean, default=False)
    account_expiry = db.Column(db.DateTime)
    id_card_image = db.Column(db.String(255))  # Required for captain and admin-student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    homeworks = db.relationship('Homework', backref='uploader', lazy=True)
    # Approvals given by this captain
    approvals_given = db.relationship('AdminStudentApproval', 
                                    backref='captain',
                                    lazy=True,
                                    foreign_keys='AdminStudentApproval.captain_id')
    # Approvals received by this admin-student
    approvals_received = db.relationship('AdminStudentApproval',
                                       backref='admin_student',
                                       lazy=True,
                                       foreign_keys='AdminStudentApproval.admin_student_id')

    def set_password(self, password):
        """Set password hash for captain and admin-student accounts."""
        if len(password) < Config.MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {Config.MIN_PASSWORD_LENGTH} characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password for captain and admin-student accounts."""
        return check_password_hash(self.password_hash, password)
    
    def is_account_expired(self):
        """Check if user account has expired."""
        return self.account_expiry and datetime.utcnow() > self.account_expiry

class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50), nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    attachment_path = db.Column(db.String(255))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    class_name = db.Column(db.String(3), nullable=False)
    section = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdminStudentApproval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    captain_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
