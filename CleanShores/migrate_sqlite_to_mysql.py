"""
CleanShores Database Migration Script: SQLite -> MySQL
Migrates existing records from the local SQLite file into MySQL.
"""
import os
import sys
import sqlite3
from datetime import datetime

# Add current folder to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from app import create_app
from models import db, User, OrganizerVerification, Drive, DriveReport, DrivePhoto, Participation, Notification, Message

def parse_dt(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(val)
    except Exception:
        pass
    for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(val, fmt)
        except Exception:
            continue
    return None

def migrate():
    sqlite_path = os.path.join(os.path.dirname(__file__), 'database', 'cleanShores.db')
    if not os.path.exists(sqlite_path):
        print(f"⚠️  No SQLite database found at: {sqlite_path}")
        return

    print("==================================================")
    print("🚀 CleanShores SQLite -> MySQL Migration")
    print(f"   Source SQLite : {sqlite_path}")
    print(f"   Target MySQL  : {Config.SQLALCHEMY_DATABASE_URI}")
    print("==================================================")

    # 1. Connect to SQLite
    s_conn = sqlite3.connect(sqlite_path)
    s_conn.row_factory = sqlite3.Row
    s_cur = s_conn.cursor()

    app = create_app()
    with app.app_context():
        # Ensure schema is ready in MySQL
        db.create_all()

        # Migrate Users
        s_cur.execute("SELECT * FROM users")
        user_rows = s_cur.fetchall()
        migrated_users = 0
        for r in user_rows:
            if not User.query.filter_by(id=r['id']).first():
                u = User(
                    id=r['id'],
                    username=r['username'],
                    email=r['email'],
                    password_hash=r['password_hash'],
                    full_name=r['full_name'],
                    phone=r['phone'],
                    role=r['role'],
                    profile_pic=r['profile_pic'],
                    bio=r['bio'],
                    location=r['location'],
                    college_or_org=r['college_or_org'],
                    skills_interests=r['skills_interests'],
                    is_active=bool(r['is_active']),
                    created_at=parse_dt(r['created_at']) or datetime.utcnow()
                )
                db.session.add(u)
                migrated_users += 1
        db.session.commit()
        print(f"✅ Migrated {migrated_users} / {len(user_rows)} Users")

        # Migrate OrganizerVerifications
        s_cur.execute("SELECT * FROM organizer_verifications")
        verif_rows = s_cur.fetchall()
        migrated_verifs = 0
        for r in verif_rows:
            if not OrganizerVerification.query.filter_by(id=r['id']).first():
                v = OrganizerVerification(
                    id=r['id'],
                    user_id=r['user_id'],
                    org_name=r['org_name'],
                    org_type=r['org_type'],
                    reg_number=r['reg_number'],
                    contact_person=r['contact_person'],
                    contact_phone=r['contact_phone'],
                    website=r['website'],
                    address=r['address'],
                    id_doc_filename=r['id_doc_filename'],
                    status=r['status'],
                    admin_remarks=r['admin_remarks'],
                    submitted_at=parse_dt(r['submitted_at']),
                    reviewed_at=parse_dt(r['reviewed_at']),
                    reviewed_by_id=r['reviewed_by_id']
                )
                db.session.add(v)
                migrated_verifs += 1
        db.session.commit()
        print(f"✅ Migrated {migrated_verifs} / {len(verif_rows)} Organizer Verifications")

        # Migrate Drives
        s_cur.execute("SELECT * FROM drives")
        drive_rows = s_cur.fetchall()
        migrated_drives = 0
        for r in drive_rows:
            if not Drive.query.filter_by(id=r['id']).first():
                d = Drive(
                    id=r['id'],
                    organizer_id=r['organizer_id'],
                    title=r['title'],
                    category=r['category'],
                    description=r['description'],
                    location_name=r['location_name'],
                    address=r['address'],
                    city=r['city'],
                    state=r['state'],
                    latitude=r['latitude'],
                    longitude=r['longitude'],
                    meeting_point=r['meeting_point'],
                    start_datetime=parse_dt(r['start_datetime']),
                    end_datetime=parse_dt(r['end_datetime']),
                    max_volunteers=r['max_volunteers'],
                    supplies_provided=r['supplies_provided'],
                    supplies_needed=r['supplies_needed'],
                    safety_guidelines=r['safety_guidelines'],
                    waste_segregation_plan=r['waste_segregation_plan'],
                    banner_image=r['banner_image'],
                    status=r['status'],
                    created_at=parse_dt(r['created_at']) or datetime.utcnow()
                )
                db.session.add(d)
                migrated_drives += 1
        db.session.commit()
        print(f"✅ Migrated {migrated_drives} / {len(drive_rows)} Drives")

        # Migrate DriveReports
        s_cur.execute("SELECT * FROM drive_reports")
        report_rows = s_cur.fetchall()
        migrated_reports = 0
        for r in report_rows:
            if not DriveReport.query.filter_by(id=r['id']).first():
                rp = DriveReport(
                    id=r['id'],
                    drive_id=r['drive_id'],
                    total_waste_kg=r['total_waste_kg'],
                    plastic_waste_kg=r['plastic_waste_kg'],
                    glass_waste_kg=r['glass_waste_kg'],
                    metal_waste_kg=r['metal_waste_kg'],
                    organic_waste_kg=r['organic_waste_kg'],
                    hazardous_waste_kg=r['hazardous_waste_kg'],
                    other_waste_kg=r['other_waste_kg'],
                    attendees_count=r['attendees_count'],
                    summary=r['summary'],
                    certificates_issued=bool(r['certificates_issued']),
                    report_file=r['report_file'],
                    created_at=parse_dt(r['created_at']) or datetime.utcnow()
                )
                db.session.add(rp)
                migrated_reports += 1
        db.session.commit()
        print(f"✅ Migrated {migrated_reports} / {len(report_rows)} Drive Reports")

        # Migrate DrivePhotos
        s_cur.execute("SELECT * FROM drive_photos")
        photo_rows = s_cur.fetchall()
        migrated_photos = 0
        for r in photo_rows:
            if not DrivePhoto.query.filter_by(id=r['id']).first():
                ph = DrivePhoto(
                    id=r['id'],
                    drive_id=r['drive_id'],
                    filename=r['filename'],
                    caption=r['caption'],
                    photo_type=r['photo_type'],
                    uploaded_at=parse_dt(r['uploaded_at']) or datetime.utcnow()
                )
                db.session.add(ph)
                migrated_photos += 1
        db.session.commit()
        print(f"✅ Migrated {migrated_photos} / {len(photo_rows)} Drive Photos")

        # Migrate Participations
        s_cur.execute("SELECT * FROM participations")
        part_rows = s_cur.fetchall()
        migrated_parts = 0
        for r in part_rows:
            if not Participation.query.filter_by(id=r['id']).first():
                pt = Participation(
                    id=r['id'],
                    drive_id=r['drive_id'],
                    volunteer_id=r['volunteer_id'],
                    status=r['status'],
                    registered_at=parse_dt(r['registered_at']) or datetime.utcnow(),
                    check_in_time=parse_dt(r['check_in_time']),
                    emergency_contact=r['emergency_contact'],
                    notes=r['notes'],
                    certificate_id=r['certificate_id'],
                    certificate_issued_at=parse_dt(r['certificate_issued_at']),
                    feedback_rating=r['feedback_rating'],
                    feedback_comment=r['feedback_comment']
                )
                db.session.add(pt)
                migrated_parts += 1
        db.session.commit()
        print(f"✅ Migrated {migrated_parts} / {len(part_rows)} Participations")

        # Migrate Notifications
        s_cur.execute("SELECT * FROM notifications")
        notif_rows = s_cur.fetchall()
        migrated_notifs = 0
        for r in notif_rows:
            if not Notification.query.filter_by(id=r['id']).first():
                nt = Notification(
                    id=r['id'],
                    user_id=r['user_id'],
                    title=r['title'],
                    message=r['message'],
                    link=r['link'],
                    notification_type=r['notification_type'],
                    is_read=bool(r['is_read']),
                    created_at=parse_dt(r['created_at']) or datetime.utcnow()
                )
                db.session.add(nt)
                migrated_notifs += 1
        db.session.commit()
        print(f"✅ Migrated {migrated_notifs} / {len(notif_rows)} Notifications")

        # Migrate Messages
        s_cur.execute("SELECT * FROM messages")
        msg_rows = s_cur.fetchall()
        migrated_msgs = 0
        for r in msg_rows:
            if not Message.query.filter_by(id=r['id']).first():
                m = Message(
                    id=r['id'],
                    sender_id=r['sender_id'],
                    recipient_id=r['recipient_id'],
                    drive_id=r['drive_id'],
                    message_text=r['message_text'],
                    is_read=bool(r['is_read']),
                    created_at=parse_dt(r['created_at']) or datetime.utcnow(),
                    is_public_qa=bool(r['is_public_qa']),
                    answer_text=r['answer_text'],
                    answered_at=parse_dt(r['answered_at'])
                )
                db.session.add(m)
                migrated_msgs += 1
        db.session.commit()
        print(f"✅ Migrated {migrated_msgs} / {len(msg_rows)} Messages")

    s_conn.close()
    print("==================================================")
    print("🎉 SQLite to MySQL Migration complete!")
    print("==================================================")

if __name__ == '__main__':
    migrate()
