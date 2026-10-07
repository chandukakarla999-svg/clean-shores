from datetime import datetime
from . import db

class Drive(db.Model):
    __tablename__ = 'drives'

    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(80), nullable=False, default='Beach Cleanup')
    description = db.Column(db.Text, nullable=False)
    location_name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='Mumbai')
    state = db.Column(db.String(100), nullable=True, default='Maharashtra')
    latitude = db.Column(db.Float, nullable=True, default=18.9220)
    longitude = db.Column(db.Float, nullable=True, default=72.8347)
    meeting_point = db.Column(db.String(200), nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    max_volunteers = db.Column(db.Integer, nullable=False, default=50)
    supplies_provided = db.Column(db.Text, nullable=True)
    supplies_needed = db.Column(db.Text, nullable=True)
    safety_guidelines = db.Column(db.Text, nullable=True)
    waste_segregation_plan = db.Column(db.Text, nullable=True)
    banner_image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='upcoming')  # 'upcoming', 'in_progress', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    participations = db.relationship('Participation', backref='drive', lazy='dynamic', cascade='all, delete-orphan')
    report = db.relationship('DriveReport', backref='drive', uselist=False, cascade='all, delete-orphan')
    photos = db.relationship('DrivePhoto', backref='drive', lazy='dynamic', cascade='all, delete-orphan')
    qa_messages = db.relationship('Message', backref='drive', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def registered_count(self):
        from .participation import Participation
        return self.participations.filter(Participation.status != 'cancelled').count()

    @property
    def attended_count(self):
        return self.participations.filter_by(status='attended').count()

    @property
    def is_full(self):
        return self.registered_count >= self.max_volunteers

    @property
    def spots_remaining(self):
        return max(0, self.max_volunteers - self.registered_count)

    @property
    def fill_percentage(self):
        if self.max_volunteers <= 0:
            return 100
        return min(100, int((self.registered_count / self.max_volunteers) * 100))

    def __repr__(self):
        return f'<Drive {self.title} - {self.status}>'


class DriveReport(db.Model):
    __tablename__ = 'drive_reports'

    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id', ondelete='CASCADE'), nullable=False, unique=True)
    total_waste_kg = db.Column(db.Float, nullable=False, default=0.0)
    plastic_waste_kg = db.Column(db.Float, nullable=False, default=0.0)
    glass_waste_kg = db.Column(db.Float, nullable=False, default=0.0)
    metal_waste_kg = db.Column(db.Float, nullable=False, default=0.0)
    organic_waste_kg = db.Column(db.Float, nullable=False, default=0.0)
    hazardous_waste_kg = db.Column(db.Float, nullable=False, default=0.0)
    other_waste_kg = db.Column(db.Float, nullable=False, default=0.0)
    attendees_count = db.Column(db.Integer, nullable=False, default=0)
    summary = db.Column(db.Text, nullable=False)
    certificates_issued = db.Column(db.Boolean, default=False)
    report_file = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DriveReport Drive {self.drive_id} - {self.total_waste_kg} kg>'


class DrivePhoto(db.Model):
    __tablename__ = 'drive_photos'

    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    photo_type = db.Column(db.String(50), default='action')  # 'before', 'after', 'action', 'segregation'
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DrivePhoto {self.filename}>'
