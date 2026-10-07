import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from models import db, OrganizerVerification
from services.notification_service import notify_verification_decision
from services.email_service import send_verification_status_email

def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'pdf', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def submit_organizer_verification(user, data, file=None):
    """
    Creates or updates the organizer's verification application.
    """
    verification = OrganizerVerification.query.filter_by(user_id=user.id).first()
    if not verification:
        verification = OrganizerVerification(user_id=user.id)
        db.session.add(verification)

    verification.org_name = data.get('org_name', user.full_name)
    verification.org_type = data.get('org_type', 'NGO')
    verification.reg_number = data.get('reg_number', '')
    verification.contact_person = data.get('contact_person', user.full_name)
    verification.contact_phone = data.get('contact_phone', user.phone)
    verification.website = data.get('website', '')
    verification.address = data.get('address', '')
    verification.status = 'pending'
    verification.submitted_at = datetime.utcnow()

    if file and file.filename and allowed_file(file.filename):
        filename = f"verify_{user.id}_{int(datetime.utcnow().timestamp())}_{secure_filename(file.filename)}"
        upload_path = os.path.join(current_app.config['VERIFICATION_UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        verification.id_doc_filename = filename

    db.session.commit()
    return verification

def review_verification(verification_id, status, remarks, admin_user):
    """
    Admin action to approve or reject organizer verification.
    """
    verification = OrganizerVerification.query.get(verification_id)
    if not verification:
        return False, "Verification record not found"

    verification.status = status
    verification.admin_remarks = remarks
    verification.reviewed_at = datetime.utcnow()
    verification.reviewed_by_id = admin_user.id
    db.session.commit()

    # Dispatch notification & email to organizer
    notify_verification_decision(verification, status, remarks)
    send_verification_status_email(verification.user, status, remarks)

    return True, f"Verification marked as {status}"
