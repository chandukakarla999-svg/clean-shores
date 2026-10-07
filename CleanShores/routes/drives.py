import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from models import db, Drive, Participation, DrivePhoto
from routes.auth import login_required

drives_bp = Blueprint('drives', __name__)


def allowed_file(filename):
    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@drives_bp.route('/drives')
def browse_drives():
    category = request.args.get('category', '')
    city = request.args.get('city', '')
    status = request.args.get('status', 'upcoming')
    search = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)

    query = Drive.query.filter(Drive.status != 'cancelled')
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter(Drive.category.ilike(f'%{category}%'))
    if city:
        query = query.filter(Drive.city.ilike(f'%{city}%'))
    if search:
        query = query.filter(
            Drive.title.ilike(f'%{search}%') |
            Drive.description.ilike(f'%{search}%') |
            Drive.location_name.ilike(f'%{search}%')
        )

    drives = query.order_by(Drive.start_datetime.asc()).paginate(page=page, per_page=9, error_out=False)

    # Fetch user's registrations if logged in
    user_registered_ids = set()
    if 'user_id' in session:
        user_participations = Participation.query.filter_by(
            volunteer_id=session['user_id']
        ).filter(Participation.status != 'cancelled').all()
        user_registered_ids = {p.drive_id for p in user_participations}

    cities = db.session.query(Drive.city).distinct().order_by(Drive.city).all()
    categories = ['Beach Cleanup', 'Urban Cleanup', 'River Cleanup', 'Park Cleanup', 'Waste Segregation Drive', 'Awareness Campaign']

    return render_template('volunteer/browse_drives.html',
                           drives=drives, user_registered_ids=user_registered_ids,
                           cities=[c[0] for c in cities], categories=categories,
                           current_category=category, current_city=city,
                           current_status=status, search_query=search)


@drives_bp.route('/drives/<int:drive_id>')
def drive_detail(drive_id):
    drive = Drive.query.get_or_404(drive_id)
    user_participation = None
    if 'user_id' in session:
        user_participation = Participation.query.filter_by(
            drive_id=drive_id, volunteer_id=session['user_id']
        ).first()
    photos = drive.photos.all()
    qa_messages = drive.qa_messages.filter_by(is_public_qa=True).order_by('created_at').all()
    return render_template('volunteer/drive_details.html',
                           drive=drive, user_participation=user_participation,
                           photos=photos, qa_messages=qa_messages)


@drives_bp.route('/drives/<int:drive_id>/register', methods=['POST'])
@login_required
def register_for_drive(drive_id):
    if session.get('role') != 'volunteer':
        flash('Only volunteers can register for drives.', 'warning')
        return redirect(url_for('drives.drive_detail', drive_id=drive_id))

    drive = Drive.query.get_or_404(drive_id)

    if drive.status != 'upcoming':
        flash('This drive is no longer accepting registrations.', 'warning')
        return redirect(url_for('drives.drive_detail', drive_id=drive_id))

    if drive.is_full:
        flash('This drive has reached its maximum capacity. Please check other drives.', 'warning')
        return redirect(url_for('drives.drive_detail', drive_id=drive_id))

    existing = Participation.query.filter_by(
        drive_id=drive_id, volunteer_id=session['user_id']
    ).first()

    if existing:
        if existing.status == 'cancelled':
            existing.status = 'registered'
            existing.registered_at = datetime.utcnow()
            db.session.commit()
            flash('You have been re-registered for this drive!', 'success')
        else:
            flash('You are already registered for this drive.', 'info')
        return redirect(url_for('drives.drive_detail', drive_id=drive_id))

    from models import User
    volunteer = User.query.get(session['user_id'])

    participation = Participation(
        drive_id=drive_id,
        volunteer_id=session['user_id'],
        emergency_contact=request.form.get('emergency_contact', ''),
        notes=request.form.get('notes', '')
    )
    db.session.add(participation)
    db.session.commit()

    # Notify organizer
    from services.notification_service import notify_organizer_registration
    from services.email_service import send_registration_confirmation, send_organizer_new_volunteer_email
    notify_organizer_registration(drive, volunteer)
    send_registration_confirmation(volunteer, drive)
    send_organizer_new_volunteer_email(drive.organizer, volunteer, drive)

    flash(f'🎉 Successfully registered for "{drive.title}"! Check your email for details.', 'success')
    return redirect(url_for('volunteer.my_registrations'))


@drives_bp.route('/drives/<int:drive_id>/cancel-registration', methods=['POST'])
@login_required
def cancel_registration(drive_id):
    participation = Participation.query.filter_by(
        drive_id=drive_id, volunteer_id=session['user_id']
    ).first_or_404()
    participation.status = 'cancelled'
    db.session.commit()
    flash('Your registration has been cancelled.', 'info')
    return redirect(url_for('volunteer.my_registrations'))


@drives_bp.route('/completed-drives')
def completed_drives():
    drives = Drive.query.filter_by(status='completed').order_by(Drive.start_datetime.desc()).all()
    # Platform stats
    total_waste = db.session.query(db.func.sum(Drive.__table__.c.id)).scalar() or 0
    return render_template('completed_drives.html', drives=drives)
