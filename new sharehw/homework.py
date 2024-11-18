from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from models import db, Homework
from utils import save_file, validate_homework_date, get_subject_choices
from datetime import datetime, timedelta
import os

homework = Blueprint('homework', __name__)

@homework.route('/homework/upload', methods=['GET', 'POST'])
@login_required
def upload():
    # Check account expiry
    if current_user.is_account_expired():
        flash('Your account has expired', 'danger')
        return redirect(url_for('auth.login'))
    
    # Only approved captains and admin-students can upload homework
    if current_user.role not in ['captain', 'admin-student'] or not current_user.is_approved:
        flash('You do not have permission to upload homework', 'danger')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        teacher_name = request.form.get('teacher_name')
        title = request.form.get('title')
        description = request.form.get('description')
        due_date = request.form.get('due_date')
        
        # Validate required fields
        if not all([subject, teacher_name, title, description, due_date]):
            flash('All fields are required', 'danger')
            return redirect(url_for('homework.upload'))
        
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('homework.upload'))
        
        # Validate due date
        is_valid, msg = validate_homework_date(due_date)
        if not is_valid:
            flash(msg, 'danger')
            return redirect(url_for('homework.upload'))
        
        # Handle file upload
        if 'attachment' not in request.files:
            flash('Homework file is required', 'danger')
            return redirect(url_for('homework.upload'))
            
        attachment = request.files['attachment']
        if attachment.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('homework.upload'))
        
        # Check file size
        if len(attachment.read()) > current_app.config['MAX_CONTENT_LENGTH']:
            flash('File size exceeds 8MB limit', 'danger')
            return redirect(url_for('homework.upload'))
        
        # Reset file pointer after reading
        attachment.seek(0)
        
        filename = save_file(attachment, current_app.config['UPLOAD_FOLDER_HOMEWORK'],
                           prefix=f"{current_user.class_name}_{current_user.section}")
        if not filename:
            flash('Invalid file type', 'danger')
            return redirect(url_for('homework.upload'))
        
        homework = Homework(
            subject=subject,
            teacher_name=teacher_name,
            title=title,
            description=description,
            due_date=due_date,
            attachment_path=filename,
            uploaded_by=current_user.id,
            class_name=current_user.class_name,
            section=current_user.section
        )
        
        try:
            db.session.add(homework)
            db.session.commit()
            flash('Homework uploaded successfully!', 'success')
            return redirect(url_for('homework.list'))
        except Exception as e:
            db.session.rollback()
            flash('Error uploading homework. Please try again.', 'danger')
            return redirect(url_for('homework.upload'))
    
    return render_template('homework/upload.html',
                         subjects=get_subject_choices(current_user.section))

@homework.route('/homework')
@login_required
def list():
    # Check account expiry
    if current_user.is_account_expired():
        flash('Your account has expired', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get filter parameters
    subject = request.args.get('subject')
    days = request.args.get('days', type=int)
    
    # Base query for user's class and section
    query = Homework.query.filter_by(
        class_name=current_user.class_name,
        section=current_user.section
    )
    
    # Apply filters
    if subject:
        query = query.filter_by(subject=subject)
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Homework.due_date >= cutoff_date)
    
    # Order by most recent first
    homeworks = query.order_by(Homework.due_date.desc()).all()
    
    return render_template('homework/list.html',
                         homeworks=homeworks,
                         subjects=get_subject_choices(current_user.section))

@homework.route('/homework/<int:id>')
@login_required
def view(id):
    homework = Homework.query.get_or_404(id)
    
    # Check if user has access to this homework
    if homework.class_name != current_user.class_name or \
       homework.section != current_user.section:
        flash('You do not have permission to view this homework', 'danger')
        return redirect(url_for('homework.list'))
    
    return render_template('homework/view.html', homework=homework)

@homework.route('/homework/<int:id>/download')
@login_required
def download(id):
    homework = Homework.query.get_or_404(id)
    
    # Check if user has access to this homework
    if homework.class_name != current_user.class_name or \
       homework.section != current_user.section:
        flash('You do not have permission to download this homework', 'danger')
        return redirect(url_for('homework.list'))
    
    # Get the directory and filename
    directory = current_app.config['UPLOAD_FOLDER_HOMEWORK']
    filename = os.path.basename(homework.attachment_path)
    
    return send_from_directory(directory, filename, as_attachment=True)

@homework.route('/homework/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    homework = Homework.query.get_or_404(id)
    
    # Only the uploader, captains, and admins can delete homework
    if homework.uploaded_by != current_user.id and \
       current_user.role not in ['captain', 'admin']:
        flash('You do not have permission to delete this homework', 'danger')
        return redirect(url_for('homework.view', id=id))
    
    db.session.delete(homework)
    db.session.commit()
    
    flash('Homework deleted successfully!', 'success')
    return redirect(url_for('homework.list'))
