from models import db, Notification

def create_notification(user_id, title, message, link=None, notification_type='system'):
    """Creates and commits an in-app notification for a user."""
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            link=link,
            notification_type=notification_type
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None

def notify_organizer_registration(drive, volunteer):
    """Notifies the drive organizer when a volunteer signs up."""
    title = f"New Volunteer: {volunteer.full_name}"
    message = f"{volunteer.full_name} has registered for '{drive.title}'. Total registered: {drive.registered_count}/{drive.max_volunteers}."
    link = f"/organizer/drives/{drive.id}/participants"
    return create_notification(drive.organizer_id, title, message, link, notification_type='registration')

def notify_volunteer_status_change(participation, status):
    """Notifies volunteer of their participation status change."""
    drive = participation.drive
    volunteer = participation.volunteer
    title = f"Drive Update: {drive.title}"
    
    if status == 'confirmed':
        message = f"Your spot for '{drive.title}' has been confirmed by the organizer! See you at {drive.location_name}."
    elif status == 'attended':
        message = f"Thank you for attending '{drive.title}'! Your contribution has been verified and your Certificate is now ready."
    elif status == 'cancelled':
        message = f"Your registration for '{drive.title}' has been cancelled."
    else:
        message = f"Your status for '{drive.title}' has been updated to {status}."
        
    link = "/volunteer/my-registrations"
    return create_notification(volunteer.id, title, message, link, notification_type='drive_update')

def notify_drive_completed(drive):
    """Notifies all attended volunteers that the impact report and certificate are available."""
    attended_participations = drive.participations.filter_by(status='attended').all()
    for p in attended_participations:
        create_notification(
            user_id=p.volunteer_id,
            title=f"Impact Report Published: {drive.title}",
            message=f"The cleanup drive report for '{drive.title}' is now live! View the total segregated waste collected and claim your certificate.",
            link=f"/drives/{drive.id}",
            notification_type='certificate'
        )

def notify_verification_decision(verification, status, remarks=None):
    """Notifies organizer when their verification status is updated by an admin."""
    title = f"Organizer Verification: {status.capitalize()}"
    if status == 'verified':
        message = "Congratulations! Your organizer credentials have been approved. You can now publish drives with a Verified badge."
    else:
        message = f"Your verification status was set to '{status}'. Admin remarks: {remarks or 'None provided'}."
    link = "/organizer/verification"
    return create_notification(verification.user_id, title, message, link, notification_type='verification')
