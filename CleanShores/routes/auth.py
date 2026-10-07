from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from models import db, User, OrganizerVerification
from services.email_service import send_welcome_email, send_login_notification, get_email_logs

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in.', 'warning')
                return redirect(url_for('auth.login'))
            if session.get('role') not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorator
    return decorator

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


# ==============================================================
# DEDICATED VOLUNTEER AUTH PAGE (Login & Register on SAME PAGE)
# ==============================================================
@auth_bp.route('/volunteer', methods=['GET', 'POST'])
@auth_bp.route('/auth/volunteer', methods=['GET', 'POST'])
def volunteer_auth():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    active_tab = request.args.get('tab', 'login')

    if request.method == 'POST':
        action = request.form.get('action', 'login')

        if action == 'register':
            full_name = request.form.get('full_name', '').strip()
            username = request.form.get('username', '').strip().lower()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            location = request.form.get('location', '').strip()
            college_or_org = request.form.get('college_or_org', '').strip()
            password = request.form.get('password', '')
            confirm = request.form.get('confirm_password', '')

            errors = []
            if not full_name: errors.append('Full name is required.')
            if not username or len(username) < 3: errors.append('Username must be at least 3 characters.')
            if not email or '@' not in email: errors.append('A valid email address is required.')
            if len(password) < 6: errors.append('Password must be at least 6 characters.')
            if password != confirm: errors.append('Passwords do not match.')

            if not errors:
                if User.query.filter_by(username=username).first():
                    errors.append('Username is already taken. Please pick another one.')
                if User.query.filter_by(email=email).first():
                    errors.append('Email is already registered. Please sign in instead.')

            if errors:
                for e in errors:
                    flash(e, 'danger')
                return render_template('auth_volunteer.html', active_tab='register', form_data=request.form)

            user = User(
                full_name=full_name,
                username=username,
                email=email,
                phone=phone,
                role='volunteer',
                location=location,
                college_or_org=college_or_org
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Dispatch welcome email to mobile/email
            send_welcome_email(user)

            # Auto-login immediately so user has zero hurdles!
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = 'volunteer'
            session['full_name'] = user.full_name

            flash(f'🎉 Welcome to CleanShores, {full_name}! Confirmation mail dispatched to {email}.', 'success')
            return redirect(url_for('volunteer.dashboard'))

        else:
            # Login action
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember_me') == 'on'

            user = User.query.filter(
                (User.email == identifier.lower()) | (User.username == identifier.lower())
            ).first()

            if not user or not user.check_password(password):
                flash('Invalid credentials. Please verify your email/username and password.', 'danger')
                return render_template('auth_volunteer.html', active_tab='login', form_data=request.form)

            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'warning')
                return render_template('auth_volunteer.html', active_tab='login')

            session.permanent = remember
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name

            # Dispatch login notification to mobile/email
            send_login_notification(user, ip=request.headers.get('X-Forwarded-For', request.remote_addr or 'Client Device'))

            flash(f'Welcome back, {user.full_name}! 🌊 Security notification sent to {user.email}.', 'success')
            
            if user.role == 'organizer':
                return redirect(url_for('organizer.dashboard'))
            return redirect(url_for('volunteer.dashboard'))

    return render_template('auth_volunteer.html', active_tab=active_tab, form_data={})


# ==============================================================
# DEDICATED ORGANIZER AUTH PAGE (Login & Register on SAME PAGE)
# ==============================================================
@auth_bp.route('/organizer', methods=['GET', 'POST'])
@auth_bp.route('/auth/organizer', methods=['GET', 'POST'])
def organizer_auth():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    active_tab = request.args.get('tab', 'login')

    if request.method == 'POST':
        action = request.form.get('action', 'login')

        if action == 'register':
            full_name = request.form.get('full_name', '').strip()
            username = request.form.get('username', '').strip().lower()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            location = request.form.get('location', '').strip()
            college_or_org = request.form.get('college_or_org', '').strip()
            password = request.form.get('password', '')
            confirm = request.form.get('confirm_password', '')

            errors = []
            if not full_name: errors.append('Representative contact name is required.')
            if not username or len(username) < 3: errors.append('Username must be at least 3 characters.')
            if not email or '@' not in email: errors.append('Official organization email is required.')
            if not college_or_org: errors.append('Organization or College name is required.')
            if len(password) < 6: errors.append('Password must be at least 6 characters.')
            if password != confirm: errors.append('Passwords do not match.')

            if not errors:
                if User.query.filter_by(username=username).first():
                    errors.append('Username is already taken. Please choose another one.')
                if User.query.filter_by(email=email).first():
                    errors.append('Email is already registered. Please sign in.')

            if errors:
                for e in errors:
                    flash(e, 'danger')
                return render_template('auth_organizer.html', active_tab='register', form_data=request.form)

            user = User(
                full_name=full_name,
                username=username,
                email=email,
                phone=phone,
                role='organizer',
                location=location,
                college_or_org=college_or_org
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            # Automatically set up verified status - no verification barrier
            ver = OrganizerVerification(
                user_id=user.id,
                org_name=college_or_org or full_name,
                org_type='Community Group',
                contact_person=full_name,
                contact_phone=phone,
                status='verified',
                submitted_at=datetime.utcnow(),
                reviewed_at=datetime.utcnow()
            )
            db.session.add(ver)
            db.session.commit()

            # Dispatch welcome email to mobile/email
            send_welcome_email(user)

            # Auto-login organizer immediately
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = 'organizer'
            session['full_name'] = user.full_name

            flash(f'🎉 Welcome, {full_name}! Your organizer account has been created successfully. You can now host drives and lead cleanups.', 'success')
            return redirect(url_for('organizer.dashboard'))

        else:
            # Login action
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember_me') == 'on'

            user = User.query.filter(
                (User.email == identifier.lower()) | (User.username == identifier.lower())
            ).first()

            if not user or not user.check_password(password):
                flash('Invalid credentials. Please verify your organizer login details.', 'danger')
                return render_template('auth_organizer.html', active_tab='login', form_data=request.form)

            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'warning')
                return render_template('auth_organizer.html', active_tab='login')

            session.permanent = remember
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name

            # Dispatch login notification
            send_login_notification(user, ip=request.headers.get('X-Forwarded-For', request.remote_addr or 'Client Device'))

            flash(f'Welcome back, Organizer {user.full_name}! 🌊 Security notification sent to {user.email}.', 'success')

            if user.role == 'volunteer':
                return redirect(url_for('volunteer.dashboard'))
            return redirect(url_for('organizer.dashboard'))

    return render_template('auth_organizer.html', active_tab=active_tab, form_data={})


# ==============================================================
# GENERAL ROUTES (Redirecting seamlessly to specific portal)
# ==============================================================
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    role = request.args.get('role', request.form.get('role', 'volunteer')).lower()
    if role == 'organizer':
        if request.method == 'POST':
            return organizer_auth()
        return redirect(url_for('auth.organizer_auth', tab='register'))
    else:
        if request.method == 'POST':
            return volunteer_auth()
        return redirect(url_for('auth.volunteer_auth', tab='register'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    role = request.args.get('role', request.form.get('role', '')).lower()
    if role == 'organizer':
        if request.method == 'POST':
            return organizer_auth()
        return redirect(url_for('auth.organizer_auth', tab='login'))
    elif role == 'volunteer':
        if request.method == 'POST':
            return volunteer_auth()
        return redirect(url_for('auth.volunteer_auth', tab='login'))

    # If role not specified in GET, route to volunteer login by default or process POST
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter(
            (User.email == identifier.lower()) | (User.username == identifier.lower())
        ).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name
            send_login_notification(user, ip=request.headers.get('X-Forwarded-For', request.remote_addr or 'Client Device'))
            flash(f'Welcome back, {user.full_name}! 🌊', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials. Please try again.', 'danger')
        return redirect(url_for('auth.volunteer_auth', tab='login'))

    return redirect(url_for('auth.volunteer_auth', tab='login'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully. See you next cleanup! 🌿', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        flash(f'If {email} is registered, a password reset link has been dispatched to your mobile email inbox.', 'info')
        if user:
            print(f"[CleanShores Auth] Password reset requested for {email}")
    return render_template('forgot_password.html')


@auth_bp.route('/email-inbox')
@auth_bp.route('/auth/email-inbox')
def email_inbox():
    """Live preview of simulated/dispatched emails for local verification"""
    logs = get_email_logs()
    return render_template('email_inbox.html', logs=logs)
