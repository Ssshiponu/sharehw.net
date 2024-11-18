from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, AdminStudentApproval
from utils import save_file, get_expiry_date, validate_password, get_section_choices
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        roll_number = request.form.get('roll_number')
        class_name = request.form.get('class_name')
        section = request.form.get('section')
        role = request.form.get('role')
        
        # Validate required fields
        if not all([full_name, roll_number, class_name, section, role]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.signup'))
            
        # Validate roll number format
        if not roll_number.isdigit() or len(roll_number) != 6:
            flash('Roll number must be 6 digits', 'danger')
            return redirect(url_for('auth.signup'))
        
        # Check if user already exists
        existing_user = User.query.filter_by(
            roll_number=roll_number,
            class_name=class_name,
            section=section
        ).first()
        
        # Handle student account update/creation
        if role == 'student':
            if existing_user:
                existing_user.full_name = full_name
                existing_user.account_expiry = get_expiry_date('student')
                db.session.commit()
                login_user(existing_user)
                flash('Account updated successfully!', 'success')
                return redirect(url_for('main.home'))
            
            user = User(
                full_name=full_name,
                roll_number=roll_number,
                class_name=class_name,
                section=section,
                role='student',
                is_approved=True,
                account_expiry=get_expiry_date('student')
            )
            
        # Handle captain/admin-student account creation
        else:
            if existing_user:
                flash('An account with this roll number already exists', 'danger')
                return redirect(url_for('auth.signup'))
                
            # Validate password
            password = request.form.get('password')
            is_valid, msg = validate_password(password)
            if not is_valid:
                flash(msg, 'danger')
                return redirect(url_for('auth.signup'))
            
            # Handle ID card upload
            if 'id_card' not in request.files:
                flash('Student ID card is required', 'danger')
                return redirect(url_for('auth.signup'))
                
            id_card = request.files['id_card']
            if id_card.filename == '':
                flash('No selected file', 'danger')
                return redirect(url_for('auth.signup'))
            
            filename = save_file(id_card, current_app.config['UPLOAD_FOLDER_ID_CARDS'], 
                               prefix=f"{role}_{roll_number}")
            if not filename:
                flash('Invalid file type', 'danger')
                return redirect(url_for('auth.signup'))
            
            user = User(
                full_name=full_name,
                roll_number=roll_number,
                class_name=class_name,
                section=section,
                role=role,
                is_approved=False,
                account_expiry=get_expiry_date(role),
                id_card_image=filename
            )
            user.set_password(password)
            
            # Create approval request for admin-student
            if role == 'admin-student':
                # Add user first to get the ID
                db.session.add(user)
                db.session.commit()
                
                captain = User.query.filter_by(
                    role='captain',
                    class_name=class_name,
                    section=section,
                    is_approved=True
                ).first()
                
                if captain:
                    approval = AdminStudentApproval(
                        admin_student_id=user.id,
                        captain_id=captain.id
                    )
                    db.session.add(approval)
                else:
                    flash('No approved captain found for your class. Please contact admin.', 'warning')
        
        if role != 'admin-student':
            db.session.add(user)
            db.session.commit()
        
        if role == 'student':
            login_user(user)
            flash('Account created successfully!', 'success')
        else:
            flash('Account created! Please wait for approval.', 'info')
        
        return redirect(url_for('main.home'))
    
    return render_template('signup.html',
                         classes=current_app.config['CLASSES'],
                         sections=get_section_choices())

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        roll_number = request.form.get('roll_number')
        class_name = request.form.get('class_name')
        section = request.form.get('section')
        password = request.form.get('password')
        
        # Find user
        user = User.query.filter_by(
            roll_number=roll_number,
            class_name=class_name,
            section=section
        ).first()
        
        if not user:
            flash('Invalid credentials or user not found', 'danger')
            return redirect(url_for('auth.login'))
        
        # Check password for captain/admin-student
        if user.role in ['captain', 'admin-student']:
            if not password or not user.check_password(password):
                flash('Invalid password', 'danger')
                return redirect(url_for('auth.login'))
            
            if not user.is_approved:
                flash('Your account is pending approval', 'warning')
                return redirect(url_for('auth.login'))
        
        # Check account expiry
        if user.is_account_expired():
            flash('Your account has expired', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('login.html',
                         classes=current_app.config['CLASSES'],
                         sections=get_section_choices())

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.home'))
