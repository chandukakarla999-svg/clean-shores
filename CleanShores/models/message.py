from datetime import datetime
from . import db

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id', ondelete='SET NULL'), nullable=True)
    message_text = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # For Drive Q&A Community Discussion
    is_public_qa = db.Column(db.Boolean, default=False)
    answer_text = db.Column(db.Text, nullable=True)
    answered_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.recipient_id}>'
