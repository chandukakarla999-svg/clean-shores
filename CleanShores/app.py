import os
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, session
from config import Config
from models import db

basedir = os.path.abspath(os.path.dirname(__file__))
static_folder_path = os.path.join(basedir, 'static')
template_folder_path = os.path.join(basedir, 'templates')

def create_app():
    app = Flask(
        __name__,
        static_folder=static_folder_path,
        static_url_path='/static',
        template_folder=template_folder_path
    )
    app.config.from_object(Config)
    app.permanent_session_lifetime = timedelta(days=7)

    # Ensure upload directories exist
    for folder in [
        app.config['UPLOAD_FOLDER'],
        app.config['VERIFICATION_UPLOAD_FOLDER'],
        app.config['DRIVE_PHOTOS_UPLOAD_FOLDER'],
        app.config['REPORTS_UPLOAD_FOLDER'],
    ]:
        os.makedirs(folder, exist_ok=True)

    # Initialize database
    db.init_app(app)

    with app.app_context():
        # Auto-create MySQL database if connecting to MySQL
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'mysql' in db_uri:
            try:
                from sqlalchemy.engine import make_url
                import pymysql
                url = make_url(db_uri)
                if url.database:
                    conn = pymysql.connect(
                        host=url.host or 'localhost',
                        port=int(url.port or 3306),
                        user=url.username or 'root',
                        password=url.password or '',
                        charset='utf8mb4',
                        connect_timeout=5
                    )
                    with conn.cursor() as cursor:
                        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{url.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                    conn.commit()
                    conn.close()
            except Exception as e:
                app.logger.warning(f"MySQL database initialization notice: {e}")

        try:
            db.create_all()
            from models import User
            if not User.query.first():
                from seed_db import seed
                seed()
        except Exception as e:
            app.logger.error(
                f"\n⚠️  Database initialization warning: {e}\n"
                f"   Connection URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}\n"
                f"   Ensure MySQL is running (e.g. XAMPP, MySQL Server) and your .env configuration is correct.\n"
            )


    # Register blueprints
    from routes.auth import auth_bp
    from routes.organizer import organizer_bp
    from routes.volunteer import volunteer_bp
    from routes.drives import drives_bp
    from routes.admin import admin_bp
    from routes.notifications import notifications_bp
    from routes.messages import messages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(organizer_bp)
    app.register_blueprint(volunteer_bp)
    app.register_blueprint(drives_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(messages_bp)

    # Main Blueprint & routes
    from flask import Blueprint
    main_bp = Blueprint('main', __name__)

    @main_bp.route('/')
    def index():
        from models import Drive, User
        upcoming_drives = Drive.query.filter_by(status='upcoming').order_by(
            Drive.start_datetime.asc()).limit(6).all()
        completed_drives = Drive.query.filter_by(status='completed').order_by(
            Drive.start_datetime.desc()).limit(3).all()
        total_users = User.query.count()
        total_drives = Drive.query.count()
        total_completed = Drive.query.filter_by(status='completed').count()

        from models import DriveReport
        waste_result = db.session.query(db.func.sum(DriveReport.total_waste_kg)).scalar()
        total_waste = round(waste_result or 0, 1)

        return render_template('index.html',
                               upcoming_drives=upcoming_drives,
                               completed_drives=completed_drives,
                               total_users=total_users,
                               total_drives=total_drives,
                               total_completed=total_completed,
                               total_waste=total_waste)

    @main_bp.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        role = session.get('role')
        if role == 'organizer':
            return redirect(url_for('organizer.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('volunteer.dashboard'))

    @main_bp.route('/about')
    def about():
        return render_template('about.html')

    app.register_blueprint(main_bp)

    # Global route aliases so url_for('index'), url_for('dashboard'), url_for('about') also resolve
    app.add_url_rule('/', 'index', view_func=index)
    app.add_url_rule('/dashboard', 'dashboard', view_func=dashboard)
    app.add_url_rule('/about', 'about', view_func=about)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Serve uploaded files
    from flask import send_from_directory
    @app.route('/uploads/drive_photos/<filename>')
    def uploaded_drive_photo(filename):
        return send_from_directory(app.config['DRIVE_PHOTOS_UPLOAD_FOLDER'], filename)

    @app.route('/uploads/verification/<filename>')
    def uploaded_verification(filename):
        if session.get('role') not in ('admin',):
            return redirect(url_for('main.index'))
        return send_from_directory(app.config['VERIFICATION_UPLOAD_FOLDER'], filename)

    @app.route('/CleanShores/static/<path:filename>')
    def cleanshores_static(filename):
        return send_from_directory(static_folder_path, filename)

    # Jinja2 globals
    @app.context_processor
    def inject_globals():
        from models import User, Notification, Message
        user = None
        unread_notifications = 0
        unread_messages = 0
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                unread_notifications = Notification.query.filter_by(
                    user_id=user.id, is_read=False).count()
                unread_messages = Message.query.filter_by(
                    recipient_id=user.id, is_read=False).count()
        return dict(
            current_user=user,
            unread_notifications=unread_notifications,
            unread_messages=unread_messages,
            now=datetime.utcnow()
        )

    @app.template_filter('timesince')
    def timesince_filter(dt):
        if not dt:
            return 'Unknown'
        now = datetime.utcnow()
        diff = now - dt
        seconds = diff.total_seconds()
        if seconds < 60:
            return 'Just now'
        elif seconds < 3600:
            return f'{int(seconds // 60)}m ago'
        elif seconds < 86400:
            return f'{int(seconds // 3600)}h ago'
        else:
            return f'{int(seconds // 86400)}d ago'

    @app.template_filter('datefmt')
    def datefmt_filter(dt, fmt='%b %d, %Y'):
        if not dt:
            return ''
        return dt.strftime(fmt)

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    print(f"🌊 CleanShores is running at http://127.0.0.1:{port}")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
