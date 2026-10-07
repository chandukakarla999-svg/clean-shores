from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Drive, Participation, Notification, Message
from routes.auth import login_required, get_current_user

volunteer_bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')


def volunteer_only(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'volunteer':
            flash('Volunteer access only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@volunteer_bp.route('/dashboard')
@volunteer_only
def dashboard():
    user = get_current_user()
    participations = Participation.query.filter_by(volunteer_id=user.id).order_by(
        Participation.registered_at.desc()).limit(5).all()
    total_registered = Participation.query.filter_by(volunteer_id=user.id).filter(
        Participation.status != 'cancelled').count()
    total_attended = Participation.query.filter_by(volunteer_id=user.id, status='attended').count()
    upcoming_drives = Participation.query.filter_by(
        volunteer_id=user.id, status='confirmed').count() + \
        Participation.query.filter_by(volunteer_id=user.id, status='registered').count()
    recent_notifications = Notification.query.filter_by(user_id=user.id, is_read=False).order_by(
        Notification.created_at.desc()).limit(5).all()
    recent_drives = Drive.query.filter_by(status='upcoming').order_by(Drive.start_datetime.asc()).limit(4).all()

    return render_template('volunteer/dashboard.html',
                           user=user,
                           participations=participations,
                           total_registered=total_registered,
                           total_attended=total_attended,
                           upcoming_drives=upcoming_drives,
                           recent_notifications=recent_notifications,
                           recent_drives=recent_drives)


@volunteer_bp.route('/my-registrations')
@volunteer_bp.route('/registrations')
@volunteer_bp.route('/my-drives')
@volunteer_only
def my_registrations():
    user = get_current_user()
    status_filter = request.args.get('status', '')
    query = Participation.query.filter_by(volunteer_id=user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    participations = query.order_by(Participation.registered_at.desc()).all()
    return render_template('volunteer/my_registrations.html',
                           user=user, participations=participations, status_filter=status_filter)


@volunteer_bp.route('/profile', methods=['GET', 'POST'])
@volunteer_only
def profile():
    user = get_current_user()
    if request.method == 'POST':
        user.full_name = request.form.get('full_name', user.full_name).strip()
        user.phone = request.form.get('phone', user.phone).strip()
        user.bio = request.form.get('bio', '').strip()
        user.location = request.form.get('location', '').strip()
        user.college_or_org = request.form.get('college_or_org', '').strip()
        user.skills_interests = request.form.get('skills_interests', '').strip()

        new_password = request.form.get('new_password', '').strip()
        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return redirect(url_for('volunteer.profile'))
            user.set_password(new_password)

        db.session.commit()
        session['full_name'] = user.full_name
        flash('Profile updated successfully! 🌿', 'success')
        return redirect(url_for('volunteer.profile'))

    return render_template('volunteer/profile.html', user=user)


@volunteer_bp.route('/notifications')
@volunteer_only
def notifications():
    user = get_current_user()
    notifs = Notification.query.filter_by(user_id=user.id).order_by(
        Notification.created_at.desc()).all()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('volunteer/notifications.html', user=user, notifications=notifs)


@volunteer_bp.route('/messages', methods=['GET', 'POST'])
@volunteer_only
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
        return redirect(url_for('volunteer.messages', **({'with': recipient_id} if recipient_id else {})))

    received = Message.query.filter_by(recipient_id=user.id).order_by(Message.created_at.desc()).all()
    sent = Message.query.filter_by(sender_id=user.id).order_by(Message.created_at.desc()).all()

    conversation_users = {}
    for m in received + sent:
        other_id = m.sender_id if m.recipient_id == user.id else m.recipient_id
        if other_id and other_id not in conversation_users:
            other_user = User.query.get(other_id)
            if other_user:
                conversation_users[other_id] = other_user

    # Get organizers of registered drives for quick contact
    my_organizers = db.session.query(User).join(Drive, User.id == Drive.organizer_id)\
        .join(Participation, Drive.id == Participation.drive_id)\
        .filter(Participation.volunteer_id == user.id, Participation.status != 'cancelled')\
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

    return render_template('volunteer/messages.html',
                           user=user, conversation_users=list(conversation_users.values()),
                           my_organizers=my_organizers,
                           selected_user=selected_user, thread_messages=thread_messages)
