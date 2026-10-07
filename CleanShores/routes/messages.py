from flask import Blueprint, jsonify, session, request
from models import db, Message, User

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/api/messages/unread-count')
def unread_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    count = Message.query.filter_by(recipient_id=session['user_id'], is_read=False).count()
    return jsonify({'count': count})
