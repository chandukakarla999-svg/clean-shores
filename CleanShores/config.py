import os
import shutil
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

IS_VERCEL = bool(os.environ.get('VERCEL'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cleanshores-default-super-secret-key-2026')
    
    # Database
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url and raw_db_url.startswith('postgres://'):
        raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)
        
    if raw_db_url:
        SQLALCHEMY_DATABASE_URI = raw_db_url
    elif IS_VERCEL:
        tmp_db = '/tmp/cleanShores.db'
        src_db = os.path.join(basedir, 'database', 'cleanShores.db')
        if not os.path.exists(tmp_db) and os.path.exists(src_db):
            try:
                shutil.copy(src_db, tmp_db)
            except Exception:
                pass
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_db}"
    else:
        db_dir = os.path.join(basedir, 'database')
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, 'cleanShores.db')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads (writable directory on Vercel is /tmp)
    if IS_VERCEL:
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
        
    VERIFICATION_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'verification')
    DRIVE_PHOTOS_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'drive_photos')
    REPORTS_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'reports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}

    # Email Settings (SMTP)
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.ethereal.email')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'True').lower() in ('true', '1', 't')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'CleanShores Platform <noreply@cleanshores.org>')
    MAIL_DEV_MODE = os.environ.get('MAIL_DEV_MODE', 'True').lower() in ('true', '1', 't')
