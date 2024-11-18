from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user
from models import db, User
from config import Config

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == Config.ADMIN_PASSWORD:
            # Create admin session
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                admin_user = User(
                    full_name='Administrator',
                    roll_number='000000',
                    class_name='NA',
                    section='NA',
                    role='admin',
                    is_approved=True
                )
                db.session.add(admin_user)
                db.session.commit()
            
            login_user(admin_user)
            return redirect(url_for('admin.dashboard'))
            
        flash('Invalid password', 'danger')
    return render_template('admin_login.html')

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))
        
    pending_captains = User.query.filter_by(role='captain', is_approved=False).all()
    pending_admin_students = User.query.filter_by(role='admin-student', is_approved=False).all()
    return render_template('admin_dashboard.html', 
                         pending_captains=pending_captains,
                         pending_admin_students=pending_admin_students)

@admin.route('/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))
        
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f'{user.full_name} has been approved', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/reject/<int:user_id>', methods=['POST'])
@login_required
def reject_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.full_name} has been rejected', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/search_users')
@login_required
def search_users():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))
        
    class_name = request.args.get('class_name')
    section = request.args.get('section')
    role = request.args.get('role')
    
    query = User.query
    
    if class_name:
        query = query.filter_by(class_name=class_name)
    if section:
        query = query.filter_by(section=section)
    if role:
        query = query.filter_by(role=role)
        
    users = query.all()
    return render_template('admin_dashboard.html', users=users)
