from flask import Blueprint, jsonify, session
from models import db, Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/api/notifications/count')
def notification_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    count = Notification.query.filter_by(user_id=session['user_id'], is_read=False).count()
    return jsonify({'count': count})


@notifications_bp.route('/api/notifications/recent')
def recent_notifications():
    if 'user_id' not in session:
        return jsonify({'notifications': []})
    notifs = Notification.query.filter_by(user_id=session['user_id']).order_by(
        Notification.created_at.desc()).limit(8).all()
    return jsonify({'notifications': [{
        'id': n.id, 'title': n.title, 'message': n.message,
        'link': n.link, 'type': n.notification_type,
        'is_read': n.is_read, 'created_at': n.created_at.strftime('%b %d, %H:%M')
    } for n in notifs]})


@notifications_bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
def mark_read(notif_id):
    if 'user_id' not in session:
        return jsonify({'success': False}), 401
    n = Notification.query.filter_by(id=notif_id, user_id=session['user_id']).first()
    if n:
        n.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404
