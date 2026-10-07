import uuid
from datetime import datetime
from . import db

class Participation(db.Model):
    __tablename__ = 'participations'

    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id', ondelete='CASCADE'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='registered')  # 'registered', 'confirmed', 'attended', 'cancelled'
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    check_in_time = db.Column(db.DateTime, nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    certificate_id = db.Column(db.String(64), unique=True, nullable=True)
    certificate_issued_at = db.Column(db.DateTime, nullable=True)
    feedback_rating = db.Column(db.Integer, nullable=True)  # 1 to 5
    feedback_comment = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('drive_id', 'volunteer_id', name='uq_drive_volunteer'),
    )

    def generate_certificate(self):
        if not self.certificate_id:
            self.certificate_id = f"CS-{uuid.uuid4().hex[:10].upper()}"
            self.certificate_issued_at = datetime.utcnow()

    def __repr__(self):
        return f'<Participation User:{self.volunteer_id} Drive:{self.drive_id} Status:{self.status}>'
