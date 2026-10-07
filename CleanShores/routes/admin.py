from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, Drive, OrganizerVerification, Participation
from routes.auth import get_current_user
from services.verification_service import review_verification
from services.email_service import get_email_logs

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_only(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Administrator access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@admin_only
def dashboard():
    admin = get_current_user()
    total_users = User.query.count()
    total_organizers = User.query.filter_by(role='organizer').count()
    total_volunteers = User.query.filter_by(role='volunteer').count()
    total_drives = Drive.query.count()
    completed_drives = Drive.query.filter_by(status='completed').count()
    upcoming_drives = Drive.query.filter_by(status='upcoming').count()
    pending_verifications = OrganizerVerification.query.filter_by(status='pending').count()
    total_participations = Participation.query.filter(Participation.status != 'cancelled').count()

    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()
    recent_drives = Drive.query.order_by(Drive.created_at.desc()).limit(5).all()
    email_logs = get_email_logs()

    return render_template('admin/dashboard.html',
                           admin=admin,
                           total_users=total_users,
                           total_organizers=total_organizers,
                           total_volunteers=total_volunteers,
                           total_drives=total_drives,
                           completed_drives=completed_drives,
                           upcoming_drives=upcoming_drives,
                           pending_verifications=pending_verifications,
                           total_participations=total_participations,
                           recent_users=recent_users,
                           recent_drives=recent_drives,
                           email_logs=email_logs)


@admin_bp.route('/organizers')
@admin_only
def organizers():
    admin = get_current_user()
    status_filter = request.args.get('status', 'pending')
    query = OrganizerVerification.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    verifications = query.order_by(OrganizerVerification.submitted_at.desc()).all()
    return render_template('admin/organizers.html', admin=admin,
                           verifications=verifications, status_filter=status_filter)


@admin_bp.route('/organizers/<int:verification_id>/review', methods=['POST'])
@admin_only
def review_organizer(verification_id):
    admin = get_current_user()
    status = request.form.get('status', 'rejected')
    remarks = request.form.get('remarks', '').strip()
    success, message = review_verification(verification_id, status, remarks, admin)
    if success:
        flash(f'✅ {message}', 'success')
    else:
        flash(f'❌ {message}', 'danger')
    return redirect(url_for('admin.organizers'))


@admin_bp.route('/drives')
@admin_only
def drives():
    admin = get_current_user()
    status_filter = request.args.get('status', '')
    query = Drive.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    drives = query.order_by(Drive.created_at.desc()).all()
    return render_template('admin/drives.html', admin=admin, drives=drives, status_filter=status_filter)


@admin_bp.route('/drives/<int:drive_id>/cancel', methods=['POST'])
@admin_only
def cancel_drive(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'cancelled'
    db.session.commit()
    flash(f'Drive "{drive.title}" has been cancelled.', 'warning')
    return redirect(url_for('admin.drives'))


@admin_bp.route('/users')
@admin_only
def users():
    admin = get_current_user()
    role_filter = request.args.get('role', '')
    search = request.args.get('q', '')
    query = User.query.filter(User.role != 'admin')
    if role_filter:
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(
            User.full_name.ilike(f'%{search}%') |
            User.email.ilike(f'%{search}%') |
            User.username.ilike(f'%{search}%')
        )
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', admin=admin, users=users,
                           role_filter=role_filter, search_query=search)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_only
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/setup-admin', methods=['GET', 'POST'])
def setup_admin():
    """One-time admin setup endpoint - only works when no admin exists."""
    if User.query.filter_by(role='admin').first():
        flash('Admin account already exists.', 'warning')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        secret_key = request.form.get('secret_key')
        if secret_key != 'CleanShores-Admin-2026':
            flash('Invalid admin setup key.', 'danger')
            return render_template('admin/setup.html')
        user = User(
            full_name='Platform Administrator',
            username='admin',
            email=request.form.get('email', 'admin@cleanshores.org'),
            role='admin',
            is_active=True
        )
        user.set_password(request.form.get('password', 'Admin@2026!'))
        db.session.add(user)
        db.session.commit()
        flash('Admin account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('admin/setup.html')
