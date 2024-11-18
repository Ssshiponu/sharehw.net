from flask import Blueprint, render_template, send_from_directory, current_app, flash, redirect, url_for
from flask_login import current_user, login_required
from models import Homework, User
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.context_processor
def utility_processor():
    """Add utility functions and variables to template context."""
    pending_approvals = 0
    if current_user.is_authenticated and current_user.role == 'admin':
        pending_approvals = User.query.filter_by(approved=False).count()
    return dict(pending_approvals=pending_approvals)

@main.route('/')
def home():
    """Home page with recent homework for authenticated users."""
    recent_homework = None
    if current_user.is_authenticated and not current_user.is_account_expired():
        # Get homework from last week
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_homework = Homework.query.filter_by(
            class_name=current_user.class_name,
            section=current_user.section
        ).filter(
            Homework.due_date >= week_ago
        ).order_by(
            Homework.due_date.desc()
        ).limit(5).all()
    
    return render_template('index.html',
                         recent_homework=recent_homework)

@main.route('/uploads/homework/<path:filename>')
def homework_file(filename):
    """Serve homework files with access control."""
    if not current_user.is_authenticated:
        return "Unauthorized", 401
    if current_user.is_account_expired():
        return "Account expired", 401
    
    return send_from_directory(current_app.config['UPLOAD_FOLDER_HOMEWORK'], filename)

@main.route('/uploads/id_cards/<path:filename>')
def id_card_file(filename):
    """Serve ID card files with admin-only access."""
    if not current_user.is_authenticated or current_user.role != 'admin':
        return "Unauthorized", 401
    
    return send_from_directory(current_app.config['UPLOAD_FOLDER_ID_CARDS'], filename)

@main.route('/profile')
@login_required
def profile():
    """User profile page."""
    if not current_user.is_authenticated:
        flash('Please login to view your profile.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('profile.html', user=current_user)
