from datetime import datetime
from . import db

class OrganizerVerification(db.Model):
    __tablename__ = 'organizer_verifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    org_name = db.Column(db.String(150), nullable=False)
    org_type = db.Column(db.String(80), nullable=False)  # 'NGO', 'College / Institute', 'Community Group', 'Eco Club', 'Individual Initiator'
    reg_number = db.Column(db.String(100), nullable=True)  # Registration / Affiliation number
    contact_person = db.Column(db.String(100), nullable=True)
    contact_phone = db.Column(db.String(25), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    address = db.Column(db.Text, nullable=True)
    id_doc_filename = db.Column(db.String(255), nullable=True)  # Proof document or letterhead
    status = db.Column(db.String(20), default='pending')  # 'unverified', 'pending', 'verified', 'rejected'
    admin_remarks = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    reviewer = db.relationship('User', foreign_keys=[reviewed_by_id])

    def __repr__(self):
        return f'<OrganizerVerification {self.org_name} - {self.status}>'
