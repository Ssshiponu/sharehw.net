import os

class Config:
    # Application Info
    APP_NAME = 'ShareHW.net'
    VERSION = '1.0.0'
    AUTHOR = 'Mohin Uddin Shipon'
    AUTHOR_CLASS = 'XI'
    AUTHOR_SECTION = 'Science-B'
    AUTHOR_ROLL = '241182'
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Shiponkarimuddin')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sharehw.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB max file size
    
    # Upload Directories
    UPLOAD_FOLDER_HOMEWORK = os.path.join('static', 'uploads', 'homework')
    UPLOAD_FOLDER_ID_CARDS = os.path.join('static', 'uploads', 'id_cards')
    
    # Admin Configuration
    ADMIN_PASSWORD = 'Sshiponkarimuddin'
    ADMIN_URL = '/admin'  # Hidden admin URL
    
    # Account Settings
    STUDENT_ACCOUNT_EXPIRY_DAYS = 730  # 2 years
    SPECIAL_ACCOUNT_EXPIRY_DAYS = 30   # 30 days for captains and admin-students
    MIN_PASSWORD_LENGTH = 8
    
    # Academic Configuration
    CLASSES = ['XI', 'XII']
    SECTIONS = {
        'Science': ['Science-A', 'Science-B'],
        'Arts': ['Arts-A', 'Arts-B',],
        'Commerce': ['Commerce-A', 'Commerce-B',]
    }
    SUBJECTS = {
        'Common': ['Bangla', 'English', 'ICT'],
        'Science': ['Physics', 'Chemistry', 'Biology', 'Higher Math', 'Agriculture'],
        'Arts': ['History', 'Geography', 'Civics', 'Economics'],
        'Commerce': ['Accounting', 'Finance', 'Business Studies', 'Economics']
    }
    
    # Homework Settings
    HOMEWORK_PAST_DAYS_LIMIT = 8  # Only allow homework from past 8 days
    ALLOWED_FILE_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
