import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from config import Config

def allowed_file(filename, allowed_extensions=None):
    """Check if the file extension is allowed."""
    if allowed_extensions is None:
        allowed_extensions = Config.ALLOWED_FILE_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, upload_folder, prefix=''):
    """Save a file to the specified upload folder with optional prefix."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if prefix:
            filename = f"{prefix}_{timestamp}_{filename}"
        else:
            filename = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return filename
    return None

def get_expiry_date(role):
    """Get account expiry date based on user role."""
    if role == 'student':
        return datetime.utcnow() + timedelta(days=Config.STUDENT_ACCOUNT_EXPIRY_DAYS)
    elif role in ['captain', 'admin-student']:
        return datetime.utcnow() + timedelta(days=Config.SPECIAL_ACCOUNT_EXPIRY_DAYS)
    return None

def validate_password(password):
    """Validate password requirements."""
    if len(password) < Config.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {Config.MIN_PASSWORD_LENGTH} characters long"
    return True, None

def format_datetime(dt):
    """Format datetime for display."""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M')
    return ''

def validate_homework_date(due_date):
    """Validate homework due date is within allowed range."""
    if not due_date:
        return False, "Due date is required"
    
    today = datetime.now().date()
    due_date = due_date.date()
    days_diff = (today - due_date).days
    
    if days_diff < 0:
        return False, "Due date cannot be in the future"
    if days_diff > Config.HOMEWORK_PAST_DAYS_LIMIT:
        return False, f"Due date cannot be more than {Config.HOMEWORK_PAST_DAYS_LIMIT} days in the past"
    return True, None

def get_section_choices():
    """Get flattened list of sections for form choices."""
    choices = []
    for stream, sections in Config.SECTIONS.items():
        choices.extend([section for section in sections])
    return choices

def get_subject_choices(section):
    """Get subject choices based on section."""
    stream = section.split('-')[0] if '-' in section else section
    subjects = Config.SUBJECTS['Common'].copy()
    
    if stream in Config.SUBJECTS:
        subjects.extend(Config.SUBJECTS[stream])
    
    return [subject for subject in subjects]
