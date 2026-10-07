import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import current_app

# In-memory history of sent/simulated emails for testing & admin portal inspection
_email_logs = []

def send_email(to_email, subject, html_content, text_content=None):
    """
    Sends an email using configured SMTP settings.
    Falls back gracefully to development logger if SMTP server is unavailable.
    """
    log_entry = {
        'to': to_email,
        'subject': subject,
        'html': html_content,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'Sent'
    }

    try:
        smtp_server = current_app.config.get('SMTP_SERVER')
        smtp_port = current_app.config.get('SMTP_PORT', 587)
        smtp_user = current_app.config.get('SMTP_USERNAME')
        smtp_pass = current_app.config.get('SMTP_PASSWORD')
        sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'CleanShores <noreply@cleanshores.org>')
        dev_mode = current_app.config.get('MAIL_DEV_MODE', True)

        # If credentials are not set or dev_mode is explicitly forced, record as simulated
        if dev_mode and not (smtp_user and smtp_pass):
            log_entry['status'] = 'Simulated (Dev Mode)'
            _email_logs.insert(0, log_entry)
            print(f"[CleanShores Email] Simulated Email to {to_email} | Subject: {subject}")
            return True

        # Attempt real SMTP delivery
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port, timeout=8)
        if current_app.config.get('SMTP_USE_TLS', True):
            server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.sendmail(sender, [to_email], msg.as_string())
        server.quit()

        log_entry['status'] = 'Delivered (SMTP)'
        _email_logs.insert(0, log_entry)
        print(f"[CleanShores Email] Successfully sent to {to_email}")
        return True

    except Exception as e:
        print(f"[CleanShores Email Warning] SMTP delivery failed: {e}. Saved to simulated mail log.")
        log_entry['status'] = f'Logged (SMTP Error: {str(e)[:40]}...)'
        _email_logs.insert(0, log_entry)
        return False


import os
from flask import request, has_request_context

def get_app_base_url():
    """Returns dynamic application base URL without hardcoding localhost."""
    try:
        if has_request_context():
            return request.host_url.rstrip('/')
    except Exception:
        pass
    env_url = os.environ.get('APP_URL') or os.environ.get('VERCEL_URL') or ''
    if env_url:
        if not env_url.startswith('http://') and not env_url.startswith('https://'):
            return f"https://{env_url.rstrip('/')}"
        return env_url.rstrip('/')
    return ''

def get_email_logs():
    return _email_logs[:50]


def send_welcome_email(user):
    subject = "Welcome to CleanShores - Empowering Environmental Action!"
    base_url = get_app_base_url()
    login_url = f"{base_url}/login" if base_url else "/login"
    html = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e0f2f1; border-radius: 12px; background: #ffffff;">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #0B2545; margin: 0; font-size: 28px;">🌊 CleanShores</h1>
            <p style="color: #00A896; font-size: 14px; margin-top: 4px; font-weight: bold;">Citizen-Driven Beach & Urban Cleanup Coordination</p>
        </div>
        <p style="font-size: 16px; color: #333333;">Hello <strong>{user.full_name}</strong>,</p>
        <p style="font-size: 15px; color: #555555; line-height: 1.6;">
            Thank you for registering on <strong>CleanShores</strong> as a <strong>{user.role.capitalize()}</strong>!
            Together, we are transforming coastlines and urban spaces into cleaner, healthier ecosystems through community action and scientific waste segregation.
        </p>
        <div style="background: #E8F5E9; border-left: 4px solid #02C39A; padding: 16px; border-radius: 6px; margin: 20px 0;">
            <p style="margin: 0; font-weight: bold; color: #1B5E20;">What you can do next:</p>
            <ul style="margin: 8px 0 0 0; padding-left: 20px; color: #2E7D32;">
                <li>{"Create cleanup drives and lead community impact" if user.role == "organizer" else "Browse upcoming beach & urban cleanup drives in your area"}</li>
                <li>Track your waste segregation impact & certificates</li>
                <li>Connect directly with verified eco-organizers & passionate volunteers</li>
            </ul>
        </div>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{login_url}" style="background: #00A896; color: #ffffff; padding: 12px 28px; border-radius: 30px; text-decoration: none; font-weight: bold; font-size: 15px;">Access Your Dashboard</a>
        </div>
        <hr style="border: 0; border-top: 1px solid #eeeeee; margin: 24px 0;">
        <p style="font-size: 12px; color: #888888; text-align: center;">CleanShores Platform &copy; 2026. Every piece of segregated waste makes an ocean of difference.</p>
    </div>
    """
    return send_email(user.email, subject, html)


def send_login_notification(user, ip=""):
    subject = "Security Alert: Successful Login to CleanShores"
    now_str = datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')
    base_url = get_app_base_url()
    rel_path = "/volunteer/dashboard" if user.role == 'volunteer' else "/organizer/dashboard"
    dashboard_url = f"{base_url}{rel_path}" if base_url else rel_path
    client_ip = ip or "Current Device"
    html = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #d1fae5; border-radius: 12px; background: #ffffff;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #0B2545; margin: 0;">🌊 CleanShores Security</h2>
            <p style="color: #028090; font-size: 13px; margin-top: 4px;">Account Login Alert</p>
        </div>
        <p style="font-size: 15px; color: #333333;">Hello <strong>{user.full_name}</strong>,</p>
        <p style="font-size: 14px; color: #555555; line-height: 1.5;">
            You have successfully signed in to your CleanShores account on your device.
        </p>
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin: 18px 0; font-size: 14px;">
            <p style="margin: 4px 0;"><strong>👤 User Account:</strong> {user.username} ({user.email})</p>
            <p style="margin: 4px 0;"><strong>🏷️ Active Role:</strong> <span style="text-transform: capitalize; color: #00A896; font-weight: bold;">{user.role}</span></p>
            <p style="margin: 4px 0;"><strong>🕒 Login Timestamp:</strong> {now_str}</p>
            <p style="margin: 4px 0;"><strong>📱 Device / IP:</strong> {client_ip}</p>
        </div>
        <p style="font-size: 13px; color: #64748b;">
            If this was you, no further action is needed! If you did not initiate this login, please reset your password immediately.
        </p>
        <div style="text-align: center; margin: 25px 0;">
            <a href="{dashboard_url}" style="background: #028090; color: #ffffff; padding: 11px 26px; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 14px;">Go to My Dashboard</a>
        </div>
        <hr style="border: 0; border-top: 1px solid #eeeeee; margin: 20px 0;">
        <p style="font-size: 11px; color: #94a3b8; text-align: center;">CleanShores Security Team &copy; 2026. Empowering clean coastal action.</p>
    </div>
    """
    return send_email(user.email, subject, html)



def send_registration_confirmation(user, drive):
    subject = f"Registration Confirmed: {drive.title}"
    base_url = get_app_base_url()
    reg_url = f"{base_url}/volunteer/my-registrations" if base_url else "/volunteer/my-registrations"
    html = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e0f2f1; border-radius: 12px; background: #ffffff;">
        <h2 style="color: #0B2545; margin-top: 0;">🎉 You are registered for {drive.title}!</h2>
        <p style="color: #555555; line-height: 1.6;">Dear {user.full_name}, your volunteer spot has been successfully confirmed.</p>
        <div style="background: #f0f7ff; border: 1px solid #b8daff; border-radius: 8px; padding: 16px; margin: 20px 0;">
            <p style="margin: 4px 0;"><strong>📍 Location:</strong> {drive.location_name}, {drive.city}</p>
            <p style="margin: 4px 0;"><strong>🚩 Meeting Point:</strong> {drive.meeting_point or 'Main entrance'}</p>
            <p style="margin: 4px 0;"><strong>🕒 Date & Time:</strong> {drive.start_datetime.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p style="margin: 4px 0;"><strong>🧤 Supplies Provided:</strong> {drive.supplies_provided or 'Gloves and garbage bags'}</p>
        </div>
        <p style="color: #666666; font-size: 14px;"><strong>Eco Tip:</strong> Please bring a reusable water bottle and wear sturdy footwear. Let's make our shores shine!</p>
        <div style="text-align: center; margin: 25px 0;">
            <a href="{reg_url}" style="background: #028090; color: #ffffff; padding: 10px 24px; border-radius: 25px; text-decoration: none; font-weight: bold;">View Your Registration Pass</a>
        </div>
    </div>
    """
    return send_email(user.email, subject, html)


def send_organizer_new_volunteer_email(organizer, volunteer, drive):
    subject = f"New Volunteer Registered: {drive.title}"
    base_url = get_app_base_url()
    mgmt_url = f"{base_url}/organizer/drives/{drive.id}/participants" if base_url else f"/organizer/drives/{drive.id}/participants"
    html = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0f2f1; border-radius: 10px;">
        <h3 style="color: #0B2545;">New Volunteer Joined Your Drive</h3>
        <p>Hello {organizer.full_name},</p>
        <p><strong>{volunteer.full_name}</strong> ({volunteer.email}) just signed up for your cleanup drive <strong>{drive.title}</strong>.</p>
        <p>Total Registered: <strong>{drive.registered_count} / {drive.max_volunteers}</strong> volunteers.</p>
        <div style="margin-top: 20px;">
            <a href="{mgmt_url}" style="background: #00A896; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none;">Manage Participants</a>
        </div>
    </div>
    """
    return send_email(organizer.email, subject, html)


def send_verification_status_email(organizer, status, remarks=None):
    subject = f"CleanShores Organizer Verification: {status.capitalize()}"
    status_color = "#02C39A" if status == "verified" else "#E76F51"
    base_url = get_app_base_url()
    verif_url = f"{base_url}/organizer/verification" if base_url else "/organizer/verification"
    html = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e0f2f1; border-radius: 12px;">
        <h2 style="color: #0B2545;">Organizer Verification Update</h2>
        <p>Dear {organizer.full_name},</p>
        <p>Your organizer verification application for <strong>CleanShores</strong> has been marked as:</p>
        <div style="font-size: 20px; font-weight: bold; color: {status_color}; padding: 12px; background: #fafafa; border-radius: 8px; text-align: center; margin: 15px 0;">
            {status.upper()}
        </div>
        {f'<p style="color: #555;"><strong>Admin Remarks:</strong> {remarks}</p>' if remarks else ''}
        <p>{"You now have full verified privileges to organize drives, recruit volunteers, and award certified impact hours." if status == "verified" else "Please review the remarks and update your verification documents."}</p>
        <a href="{verif_url}" style="background: #00A896; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block; margin-top: 15px;">Check Verification Status</a>
    </div>
    """
    return send_email(organizer.email, subject, html)


def send_completion_certificate_email(volunteer, drive, certificate_id):
    subject = f"Certificate of Contribution: {drive.title}"
    base_url = get_app_base_url()
    cert_url = f"{base_url}/volunteer/my-registrations" if base_url else "/volunteer/my-registrations"
    html = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 2px solid #00A896; border-radius: 12px; background: #ffffff;">
        <h2 style="color: #0B2545; text-align: center;">🏅 Certificate of Eco-Contribution</h2>
        <p style="text-align: center; color: #555;">CleanShores Citizen Impact Recognition</p>
        <p>Dear {volunteer.full_name},</p>
        <p>Thank you for your active participation in <strong>{drive.title}</strong>! Your dedication helped clean our environment and segregate critical waste materials.</p>
        <div style="text-align: center; margin: 20px 0; padding: 15px; background: #f0fdf4; border-radius: 8px;">
            <p style="margin: 0; font-size: 13px; color: #166534;">Certificate ID</p>
            <p style="margin: 4px 0; font-size: 22px; font-weight: bold; color: #028090; letter-spacing: 2px;">{certificate_id}</p>
        </div>
        <div style="text-align: center; margin-top: 25px;">
            <a href="{cert_url}" style="background: #02C39A; color: white; padding: 12px 28px; border-radius: 25px; text-decoration: none; font-weight: bold;">View & Download Certificate</a>
        </div>
    </div>
    """
    return send_email(volunteer.email, subject, html)

