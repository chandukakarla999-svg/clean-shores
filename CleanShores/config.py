import os
import shutil
from urllib.parse import quote_plus
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

IS_VERCEL = bool(os.environ.get('VERCEL'))

def is_mysql_reachable(host, port):
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect((host, int(port)))
        s.close()
        return True
    except Exception:
        return False

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cleanshores-default-super-secret-key-2026')
    
    # Database: MySQL is the primary storage engine
    raw_db_url = os.environ.get('DATABASE_URL')
    force_mysql = os.environ.get('FORCE_MYSQL', 'false').lower() in ('true', '1', 't')

    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', '')
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = os.environ.get('MYSQL_PORT', '3306')
    mysql_db = os.environ.get('MYSQL_DATABASE', os.environ.get('MYSQL_DB', 'cleanshores_db'))
    
    if mysql_password:
        auth = f"{mysql_user}:{quote_plus(mysql_password)}"
    else:
        auth = mysql_user
    mysql_constructed = f"mysql+pymysql://{auth}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4"

    if IS_VERCEL:
        tmp_db = '/tmp/cleanShores.db'
        src_db = os.path.join(basedir, 'database', 'cleanShores.db')
        if not os.path.exists(tmp_db) and os.path.exists(src_db):
            try:
                shutil.copy(src_db, tmp_db)
            except Exception:
                pass
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_db}"
    elif raw_db_url and ('postgres' in raw_db_url or 'sqlite' in raw_db_url):
        if raw_db_url.startswith('postgres://'):
            raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        target_mysql_url = raw_db_url if (raw_db_url and 'mysql' in raw_db_url) else mysql_constructed
        if target_mysql_url.startswith('mysql://'):
            target_mysql_url = target_mysql_url.replace('mysql://', 'mysql+pymysql://', 1)

        # Check if MySQL server is reachable or forced
        if is_mysql_reachable(mysql_host, mysql_port) or force_mysql:
            SQLALCHEMY_DATABASE_URI = target_mysql_url
        else:
            db_dir = os.path.join(basedir, 'database')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'cleanShores.db')
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
            print(f"ℹ️  MySQL ({mysql_host}:{mysql_port}) is not currently active. Seamlessly serving preview from {db_path}.")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }



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
