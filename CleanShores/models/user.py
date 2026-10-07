from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='volunteer')  # 'organizer', 'volunteer', 'admin'
    profile_pic = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(120), nullable=True)
    college_or_org = db.Column(db.String(150), nullable=True)
    skills_interests = db.Column(db.String(255), nullable=True)  # e.g., 'Waste Segregation, First Aid, Photography'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    drives_organized = db.relationship('Drive', backref='organizer', lazy='dynamic', cascade='all, delete-orphan')
    participations = db.relationship('Participation', backref='volunteer', lazy='dynamic', cascade='all, delete-orphan')
    verification = db.relationship('OrganizerVerification', foreign_keys='OrganizerVerification.user_id', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_verified(self):
        if self.role in ('admin', 'organizer'):
            return True
        return False

    @property
    def verification_status(self):
        if self.role in ('admin', 'organizer'):
            return 'verified'
        return 'not_applicable'

    @property
    def total_attended_drives(self):
        return self.participations.filter_by(status='attended').count()

    @property
    def total_volunteer_hours(self):
        # Calculate hours based on attended drives
        attended = self.participations.filter_by(status='attended').all()
        hours = 0
        for p in attended:
            if p.drive:
                duration = (p.drive.end_datetime - p.drive.start_datetime).total_seconds() / 3600.0
                hours += max(1.0, round(duration, 1))
        return round(hours, 1)

    @property
    def badges(self):
        earned = []
        attended_count = self.total_attended_drives
        if attended_count >= 1:
            earned.append({
                'name': 'Pioneer Scout',
                'desc': 'Participated in your first CleanShores cleanup drive!',
                'icon': 'fa-solid fa-seedling',
                'color': '#02C39A'
            })
        if attended_count >= 3:
            earned.append({
                'name': 'Coastline Guardian',
                'desc': 'Completed 3+ beach and urban cleanup operations.',
                'icon': 'fa-solid fa-water',
                'color': '#00A896'
            })
        if attended_count >= 5:
            earned.append({
                'name': 'Zero-Waste Champion',
                'desc': 'Veteran volunteer who has diverted over 50kg of plastic!',
                'icon': 'fa-solid fa-recycle',
                'color': '#F4A261'
            })
        if self.role == 'organizer':
            completed_drives = self.drives_organized.filter_by(status='completed').count()
            if completed_drives >= 1:
                earned.append({
                    'name': 'Drive Commander',
                    'desc': 'Successfully organized and completed a certified cleanup drive.',
                    'icon': 'fa-solid fa-bullhorn',
                    'color': '#134074'
                })
        return earned

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
