from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .verification import OrganizerVerification
from .drive import Drive, DriveReport, DrivePhoto
from .participation import Participation
from .notification import Notification
from .message import Message

__all__ = [
    'db',
    'User',
    'OrganizerVerification',
    'Drive',
    'DriveReport',
    'DrivePhoto',
    'Participation',
    'Notification',
    'Message'
]
