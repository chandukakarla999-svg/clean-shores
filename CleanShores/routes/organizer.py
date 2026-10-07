import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from models import db, User, Drive, Participation, Notification, Message, DriveReport, DrivePhoto, OrganizerVerification
from routes.auth import login_required, role_required, get_current_user
from services.verification_service import submit_organizer_verification

organizer_bp = Blueprint('organizer', __name__, url_prefix='/organizer')


def organizer_only(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'organizer':
            flash('Organizer access only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@organizer_bp.route('/dashboard')
@organizer_only
def dashboard():
    user = get_current_user()
    drives = Drive.query.filter_by(organizer_id=user.id).order_by(Drive.created_at.desc()).limit(5).all()
    total_drives = Drive.query.filter_by(organizer_id=user.id).count()
    upcoming_drives = Drive.query.filter_by(organizer_id=user.id, status='upcoming').count()
    completed_drives = Drive.query.filter_by(organizer_id=user.id, status='completed').count()

    # Count total volunteers across all drives
    total_volunteers = db.session.query(db.func.count(Participation.id)).join(Drive).filter(
        Drive.organizer_id == user.id,
        Participation.status != 'cancelled'
    ).scalar() or 0

    recent_notifications = Notification.query.filter_by(user_id=user.id, is_read=False).order_by(
        Notification.created_at.desc()).limit(5).all()

    return render_template('organizer/dashboard.html',
                           user=user, drives=drives,
                           total_drives=total_drives,
                           upcoming_drives=upcoming_drives,
                           completed_drives=completed_drives,
                           total_volunteers=total_volunteers,
                           recent_notifications=recent_notifications)


@organizer_bp.route('/verification', methods=['GET', 'POST'])
@organizer_only
def verification():
    user = get_current_user()
    verification = OrganizerVerification.query.filter_by(user_id=user.id).first()
    if not verification:
        verification = OrganizerVerification(
            user_id=user.id,
            org_name=user.college_or_org or user.full_name,
            org_type='Community Group',
            contact_person=user.full_name,
            contact_phone=user.phone or '',
            status='verified',
            submitted_at=datetime.utcnow(),
            reviewed_at=datetime.utcnow()
        )
        db.session.add(verification)
        db.session.commit()

    if request.method == 'POST':
        file = request.files.get('id_doc')
        data = {
            'org_name': request.form.get('org_name'),
            'org_type': request.form.get('org_type'),
            'reg_number': request.form.get('reg_number'),
            'contact_person': request.form.get('contact_person'),
            'contact_phone': request.form.get('contact_phone'),
            'website': request.form.get('website'),
            'address': request.form.get('address'),
        }
        submit_organizer_verification(user, data, file)
        flash('✅ Verification request submitted! Admin will review within 24-48 hours.', 'success')
        return redirect(url_for('organizer.verification'))

    return render_template('organizer/verification.html', user=user, verification=verification)


@organizer_bp.route('/create-drive', methods=['GET', 'POST'])
@organizer_only
def create_drive():
    user = get_current_user()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Beach Cleanup')
        description = request.form.get('description', '').strip()
        location_name = request.form.get('location_name', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        meeting_point = request.form.get('meeting_point', '').strip()
        start_dt_str = request.form.get('start_datetime', '')
        end_dt_str = request.form.get('end_datetime', '')
        max_volunteers = int(request.form.get('max_volunteers', 50))
        supplies_provided = request.form.get('supplies_provided', '').strip()
        supplies_needed = request.form.get('supplies_needed', '').strip()
        safety_guidelines = request.form.get('safety_guidelines', '').strip()
        waste_segregation_plan = request.form.get('waste_segregation_plan', '').strip()

        errors = []
        if not title: errors.append('Drive title is required.')
        if not description: errors.append('Description is required.')
        if not location_name: errors.append('Location name is required.')
        if not city: errors.append('City is required.')

        try:
            start_dt = datetime.strptime(start_dt_str, '%Y-%m-%dT%H:%M')
            end_dt = datetime.strptime(end_dt_str, '%Y-%m-%dT%H:%M')
            if end_dt <= start_dt:
                errors.append('End time must be after start time.')
        except ValueError:
            errors.append('Valid start and end dates/times are required.')
            start_dt = end_dt = datetime.utcnow()

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('organizer/create_drive.html', user=user, form_data=request.form)

        drive = Drive(
            organizer_id=user.id, title=title, category=category,
            description=description, location_name=location_name, address=address,
            city=city, state=state, meeting_point=meeting_point,
            start_datetime=start_dt, end_datetime=end_dt,
            max_volunteers=max_volunteers,
            supplies_provided=supplies_provided, supplies_needed=supplies_needed,
            safety_guidelines=safety_guidelines, waste_segregation_plan=waste_segregation_plan
        )

        banner = request.files.get('banner_image')
        if banner and banner.filename and allowed_file(banner.filename):
            filename = f"banner_{user.id}_{int(datetime.utcnow().timestamp())}_{secure_filename(banner.filename)}"
            save_path = os.path.join(current_app.config['DRIVE_PHOTOS_UPLOAD_FOLDER'], filename)
            banner.save(save_path)
            drive.banner_image = filename

        db.session.add(drive)
        db.session.commit()
        flash(f'🌊 Drive "{drive.title}" created successfully!', 'success')
        return redirect(url_for('organizer.my_drives'))

    return render_template('organizer/create_drive.html', user=user, form_data={})


@organizer_bp.route('/my-drives')
@organizer_only
def my_drives():
    user = get_current_user()
    status_filter = request.args.get('status', '')
    query = Drive.query.filter_by(organizer_id=user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    drives = query.order_by(Drive.start_datetime.desc()).all()
    return render_template('organizer/my_drives.html', user=user, drives=drives, status_filter=status_filter)


@organizer_bp.route('/drives/<int:drive_id>/participants')
@organizer_only
def participants(drive_id):
    user = get_current_user()
    drive = Drive.query.filter_by(id=drive_id, organizer_id=user.id).first_or_404()
    participations = Participation.query.filter_by(drive_id=drive_id).join(User).order_by(Participation.registered_at.desc()).all()
    return render_template('organizer/participants.html', user=user, drive=drive, participations=participations)


@organizer_bp.route('/drives/<int:drive_id>/participants/<int:part_id>/status', methods=['POST'])
@organizer_only
def update_participant_status(drive_id, part_id):
    user = get_current_user()
    drive = Drive.query.filter_by(id=drive_id, organizer_id=user.id).first_or_404()
    participation = Participation.query.get_or_404(part_id)
    new_status = request.form.get('status')

    if new_status in ('registered', 'confirmed', 'attended', 'cancelled'):
        participation.status = new_status
        if new_status == 'attended':
            participation.check_in_time = datetime.utcnow()
            participation.generate_certificate()
            from services.email_service import send_completion_certificate_email
            send_completion_certificate_email(participation.volunteer, drive, participation.certificate_id)
        db.session.commit()
        from services.notification_service import notify_volunteer_status_change
        notify_volunteer_status_change(participation, new_status)
        flash(f'Participant status updated to "{new_status}".', 'success')

    return redirect(url_for('organizer.participants', drive_id=drive_id))


@organizer_bp.route('/drives/<int:drive_id>/complete', methods=['GET', 'POST'])
@organizer_only
def complete_drive(drive_id):
    user = get_current_user()
    drive = Drive.query.filter_by(id=drive_id, organizer_id=user.id).first_or_404()

    if request.method == 'POST':
        total_waste = float(request.form.get('total_waste_kg', 0))
        plastic = float(request.form.get('plastic_waste_kg', 0))
        glass = float(request.form.get('glass_waste_kg', 0))
        metal = float(request.form.get('metal_waste_kg', 0))
        organic = float(request.form.get('organic_waste_kg', 0))
        hazardous = float(request.form.get('hazardous_waste_kg', 0))
        other = float(request.form.get('other_waste_kg', 0))
        attendees_count = int(request.form.get('attendees_count', 0))
        summary = request.form.get('summary', '').strip()

        report = DriveReport(
            drive_id=drive_id,
            total_waste_kg=total_waste,
            plastic_waste_kg=plastic,
            glass_waste_kg=glass,
            metal_waste_kg=metal,
            organic_waste_kg=organic,
            hazardous_waste_kg=hazardous,
            other_waste_kg=other,
            attendees_count=attendees_count,
            summary=summary
        )
        db.session.add(report)
        drive.status = 'completed'

        # Upload photos
        photos = request.files.getlist('photos')
        for photo in photos:
            if photo and photo.filename and allowed_file(photo.filename):
                fname = f"drive_{drive_id}_{int(datetime.utcnow().timestamp())}_{secure_filename(photo.filename)}"
                fpath = os.path.join(current_app.config['DRIVE_PHOTOS_UPLOAD_FOLDER'], fname)
                photo.save(fpath)
                dp = DrivePhoto(drive_id=drive_id, filename=fname)
                db.session.add(dp)

        db.session.commit()

        from services.notification_service import notify_drive_completed
        notify_drive_completed(drive)

        flash(f'🎊 Drive "{drive.title}" marked as completed with impact report!', 'success')
        return redirect(url_for('organizer.my_drives'))

    return render_template('organizer/complete_drive.html', user=user, drive=drive)


@organizer_bp.route('/notifications')
@organizer_only
def notifications():
    user = get_current_user()
    notifs = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    # Mark all as read
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('organizer/notifications.html', user=user, notifications=notifs)


@organizer_bp.route('/messages', methods=['GET', 'POST'])
@organizer_only
def messages():
    user = get_current_user()
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id', type=int)
        message_text = request.form.get('message_text', '').strip()
        if recipient_id and message_text:
            msg = Message(sender_id=user.id, recipient_id=recipient_id, message_text=message_text)
            db.session.add(msg)
            db.session.commit()
            flash('Message sent!', 'success')
        return redirect(url_for('organizer.messages'))

    # Get all conversations
    received = Message.query.filter_by(recipient_id=user.id).order_by(Message.created_at.desc()).all()
    sent = Message.query.filter_by(sender_id=user.id).order_by(Message.created_at.desc()).all()

    # Build conversation list (unique users)
    conversation_users = {}
    for m in received + sent:
        other_id = m.sender_id if m.recipient_id == user.id else m.recipient_id
        if other_id and other_id not in conversation_users:
            other_user = User.query.get(other_id)
            if other_user:
                conversation_users[other_id] = other_user

    # Fetch volunteers registered for organizer's drives (for new messages)
    drive_volunteers = db.session.query(User).join(Participation, User.id == Participation.volunteer_id)\
        .join(Drive, Drive.id == Participation.drive_id)\
        .filter(Drive.organizer_id == user.id, Participation.status != 'cancelled')\
        .distinct().all()

    selected_user_id = request.args.get('with', type=int)
    selected_user = None
    thread_messages = []
    if selected_user_id:
        selected_user = User.query.get(selected_user_id)
        thread_messages = Message.query.filter(
            ((Message.sender_id == user.id) & (Message.recipient_id == selected_user_id)) |
            ((Message.sender_id == selected_user_id) & (Message.recipient_id == user.id))
        ).order_by(Message.created_at.asc()).all()
        for m in thread_messages:
            if m.recipient_id == user.id:
                m.is_read = True
        db.session.commit()

    return render_template('organizer/messages.html',
                           user=user, conversation_users=list(conversation_users.values()),
                           drive_volunteers=drive_volunteers,
                           selected_user=selected_user, thread_messages=thread_messages)
