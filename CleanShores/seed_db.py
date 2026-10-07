from datetime import datetime, timedelta
import os
from models import db, User, OrganizerVerification, Drive, DriveReport, DrivePhoto, Participation, Notification, Message

def seed():
    from flask import current_app
    if current_app:
        _run_seed()
    else:
        from app import create_app
        _app = create_app()
        with _app.app_context():
            _run_seed()

def _run_seed():
    if True:
        db.create_all()

        # Check if already seeded
        if User.query.filter_by(username='admin').first():
            print("Database already seeded.")
            return

        print("Seeding CleanShores database...")

        # 1. Admin
        admin = User(
            full_name='System Administrator',
            username='admin',
            email='admin@cleanshores.org',
            role='admin',
            location='Mumbai, Maharashtra',
            is_active=True
        )
        admin.set_password('Admin@2026!')
        db.session.add(admin)

        # 2. Organizers
        org1 = User(
            full_name='Ocean Care Foundation',
            username='oceancare',
            email='contact@oceancare.org',
            phone='+91 98201 12345',
            role='organizer',
            college_or_org='Ocean Care Foundation (Registered NGO)',
            location='Mumbai, Maharashtra',
            bio='Dedicated to preserving marine life and coastlines across Western India through community action.',
            is_active=True
        )
        org1.set_password('Org@2026!')
        db.session.add(org1)

        org2 = User(
            full_name='St. Xavier Eco Club',
            username='xaviers_eco',
            email='eco@xaviers.edu',
            phone='+91 98111 22334',
            role='organizer',
            college_or_org="St. Xavier's College",
            location='Mumbai, Maharashtra',
            bio='Student-led environmental sustainability coalition tackling urban and coastal debris.',
            is_active=True
        )
        org2.set_password('Org@2026!')
        db.session.add(org2)

        org3 = User(
            full_name='Goa Coastal Guardians',
            username='goacoastal',
            email='hello@goacoastal.org',
            phone='+91 97654 32100',
            role='organizer',
            college_or_org='Goa Coastal Guardians Community NGO',
            location='Panaji, Goa',
            bio='Preserving Goa pristine shores through weekly citizen cleanups and microplastic audits.',
            is_active=True
        )
        org3.set_password('Org@2026!')
        db.session.add(org3)

        org_pending = User(
            full_name='Kovalam Clean Wave',
            username='kovalamwave',
            email='team@kovalamwave.in',
            phone='+91 94471 88990',
            role='organizer',
            college_or_org='Kovalam Clean Wave Eco Initiative',
            location='Thiruvananthapuram, Kerala',
            bio='Community collective organizing surf beach and backwater waste removal in South Kerala.',
            is_active=True
        )
        org_pending.set_password('Org@2026!')
        db.session.add(org_pending)

        # 3. Volunteers
        vol1 = User(
            full_name='Aarav Sharma',
            username='aarav',
            email='aarav.sharma@example.com',
            phone='+91 99887 76655',
            role='volunteer',
            college_or_org='IIT Bombay Eco Group',
            location='Mumbai, Maharashtra',
            skills_interests='Waste Segregation, First Aid, Team Lead',
            bio='Passionate environmentalist and engineering student committed to cleaner oceans.',
            is_active=True
        )
        vol1.set_password('Vol@2026!')
        db.session.add(vol1)

        vol2 = User(
            full_name='Priya Patel',
            username='priyapatel',
            email='priya.patel@example.com',
            phone='+91 91234 56789',
            role='volunteer',
            college_or_org='K.J. Somaiya College',
            location='Mumbai, Maharashtra',
            skills_interests='Photography, Social Media, Marine Biology',
            bio='Nature photographer and volunteer documentarian capturing shoreline recovery.',
            is_active=True
        )
        vol2.set_password('Vol@2026!')
        db.session.add(vol2)

        vol3 = User(
            full_name='Rohan Mehta',
            username='rohanmehta',
            email='rohan.mehta@example.com',
            phone='+91 98765 43210',
            role='volunteer',
            college_or_org='Goa University',
            location='Panaji, Goa',
            skills_interests='Waste Segregation, Heavy Lifting, Logistics',
            bio='Surfer and beach lover defending coastal habitats.',
            is_active=True
        )
        vol3.set_password('Vol@2026!')
        db.session.add(vol3)

        db.session.commit()

        # 4. Verifications
        ver1 = OrganizerVerification(
            user_id=org1.id,
            org_name='Ocean Care Foundation',
            org_type='NGO',
            reg_number='NGO-MH-2018-84729',
            contact_person='Sunil Deshmukh',
            contact_phone='+91 98201 12345',
            website='https://oceancare.org',
            address='Suite 402, Marine Chambers, Nariman Point, Mumbai 400021',
            status='verified',
            admin_remarks='Verified official NGO credentials with government registry.',
            reviewed_by_id=admin.id,
            reviewed_at=datetime.utcnow()
        )
        db.session.add(ver1)

        ver2 = OrganizerVerification(
            user_id=org2.id,
            org_name="St. Xavier's College Eco Club",
            org_type='College / Institute',
            reg_number='INST-SXC-2022-019',
            contact_person='Dr. Maya Sen',
            contact_phone='+91 98111 22334',
            website='https://xaviers.edu/eco',
            address='5 Mahapalika Marg, Dhobi Talao, Mumbai 400001',
            status='verified',
            admin_remarks='Verified official college faculty advisor endorsement.',
            reviewed_by_id=admin.id,
            reviewed_at=datetime.utcnow()
        )
        db.session.add(ver2)

        ver3 = OrganizerVerification(
            user_id=org3.id,
            org_name='Goa Coastal Guardians',
            org_type='Community Group',
            reg_number='COMM-GOA-2023-410',
            contact_person='Alok Fernandes',
            contact_phone='+91 97654 32100',
            website='https://goacoastal.org',
            address='Miramar Beach Road, Panaji, Goa 403001',
            status='verified',
            admin_remarks='Verified active community record and past drive reports.',
            reviewed_by_id=admin.id,
            reviewed_at=datetime.utcnow()
        )
        db.session.add(ver3)

        ver_pending = OrganizerVerification(
            user_id=org_pending.id,
            org_name='Kovalam Clean Wave',
            org_type='Eco Club',
            reg_number='ECO-KER-2026-992',
            contact_person='Vipin Nair',
            contact_phone='+91 94471 88990',
            website='https://kovalamcleanwave.in',
            address='Light House Beach Walkway, Kovalam, Thiruvananthapuram 695527',
            status='verified',
            submitted_at=datetime.utcnow() - timedelta(days=1),
            reviewed_at=datetime.utcnow(),
            reviewed_by_id=admin.id
        )
        db.session.add(ver_pending)

        db.session.commit()

        # 5. Drives
        now = datetime.utcnow()
        drive1 = Drive(
            organizer_id=org1.id,
            title='Mega Girgaon Chowpatty Plastic Interception',
            category='Beach Cleanup',
            description='Join Ocean Care Foundation for a high-impact morning cleanup targeting festival debris and single-use microplastics along Girgaon Chowpatty. Gloves, gunny bags, water refill stations, and certified weighing scales provided.',
            location_name='Girgaon Chowpatty (Near Bandstand)',
            address='Marine Drive, Girgaon, Mumbai, Maharashtra 400004',
            city='Mumbai',
            state='Maharashtra',
            latitude=18.9548,
            longitude=72.8154,
            meeting_point='Opposite Mafatlal Swimming Club entrance, look for CleanShores canopy flag',
            start_datetime=now + timedelta(days=3, hours=2),
            end_datetime=now + timedelta(days=3, hours=5),
            max_volunteers=60,
            supplies_provided='High-grade puncture-resistant nitrile gloves, jute collection sacks, trash grabbers, first-aid kits, electrolyte drinks.',
            supplies_needed='Sun cap, refillable water bottle, closed sturdy shoes (no slippers), eco-conscious mindset.',
            safety_guidelines='Do not handle broken glass or syringes with bare hands; use grabbers. Stay together in teams of 4.',
            waste_segregation_plan='Separate 4 streams: (1) Rigid plastics, (2) Multi-layered plastic wrappers, (3) Glass & footwear, (4) Organic coconut shells.',
            status='upcoming'
        )
        db.session.add(drive1)

        drive2 = Drive(
            organizer_id=org2.id,
            title='Mahim Beach Mangrove Edge Plastic Cleansing',
            category='Beach Cleanup',
            description='Targeting the high-tide debris trapped between the Mahim bay sands and mangrove fringes. Crucial drive to protect fish breeding nurseries and stop marine entanglement.',
            location_name='Mahim Beach Causeway End',
            address='Reti Bunder, Mahim West, Mumbai, Maharashtra 400016',
            city='Mumbai',
            state='Maharashtra',
            latitude=19.0434,
            longitude=72.8397,
            meeting_point='Mahim Dargah Seaside Promontory checkpoint',
            start_datetime=now + timedelta(days=6, hours=1),
            end_datetime=now + timedelta(days=6, hours=4),
            max_volunteers=45,
            supplies_provided='Heavy-duty mud boots, biodegradable bags, sharps containers, hand sanitizers.',
            supplies_needed='Rubber boots if available, full-length pants, reusable water bottle.',
            safety_guidelines='Watch your step on wet sand and tidal rocks. Do not pull debris tangled tightly around mangrove roots.',
            waste_segregation_plan='Plastic bottles, synthetic ropes/nets, Styrofoam, and general waste separated on tarpaulins.',
            status='upcoming'
        )
        db.session.add(drive2)

        drive3 = Drive(
            organizer_id=org3.id,
            title='Miramar Sunset Shoreline Sweep & Microplastic Audit',
            category='Beach Cleanup',
            description='Community clean sweep along Miramar beach sands. Combined with a volunteer citizen-science audit of bottle caps, cigarette butts, and microplastics.',
            location_name='Miramar Beach',
            address='Miramar, Panaji, Goa 403001',
            city='Panaji',
            state='Goa',
            latitude=15.4822,
            longitude=73.8077,
            meeting_point='Miramar Circle Statue, adjacent to the lifeguard tower',
            start_datetime=now + timedelta(days=10, hours=9),
            end_datetime=now + timedelta(days=10, hours=12),
            max_volunteers=50,
            supplies_provided='Audit sifting screens, reusable gloves, collection bins, cold tender coconut water.',
            supplies_needed='Wide-brim hat, comfortable walking clothes, mobile camera for audit logging.',
            safety_guidelines='Stay clear of sudden waves. Report any stranded marine creatures immediately to lifeguards.',
            waste_segregation_plan='Micro-plastics sifted separately; recyclables sent to Panaji Municipal MRF.',
            status='upcoming'
        )
        db.session.add(drive3)

        drive_completed = Drive(
            organizer_id=org1.id,
            title='Versova Beach Weekend Deep Cleanup Phase IV',
            category='Beach Cleanup',
            description='Massive citizen action along the northern rocky stretch of Versova Beach. Over 30 volunteers mobilized and cleared centuries of compacted marine debris.',
            location_name='Versova Beach (North End)',
            address='Versova, Andheri West, Mumbai, Maharashtra 400061',
            city='Mumbai',
            state='Maharashtra',
            latitude=19.1363,
            longitude=72.8093,
            meeting_point='Versova Koliwada Jetty entrance',
            start_datetime=now - timedelta(days=5, hours=4),
            end_datetime=now - timedelta(days=5, hours=1),
            max_volunteers=40,
            supplies_provided='Full safety gear, heavy grabbers, hydration counter, medical standby.',
            supplies_needed='Enthusiasm, sturdy shoes.',
            safety_guidelines='Teamwork and safety protocol observed.',
            waste_segregation_plan='Municipal dry waste truck on-site for segregated handoff.',
            status='completed'
        )
        db.session.add(drive_completed)

        db.session.commit()

        # 6. Report for Completed Drive
        report1 = DriveReport(
            drive_id=drive_completed.id,
            total_waste_kg=485.5,
            plastic_waste_kg=295.0,
            glass_waste_kg=78.5,
            metal_waste_kg=32.0,
            organic_waste_kg=55.0,
            hazardous_waste_kg=12.0,
            other_waste_kg=13.0,
            attendees_count=32,
            summary='Phenomenal community turnout! We cleared a heavily degraded 350-meter stretch of Versova coastline. Over 295 kg of plastic packaging and derelict fishing nets were diverted directly to certified recyclers in partnership with BMC Ward K-West. Certificates generated and awarded to all verified attendees.',
            certificates_issued=True
        )
        db.session.add(report1)

        # 7. Participations
        p1 = Participation(
            drive_id=drive_completed.id,
            volunteer_id=vol1.id,
            status='attended',
            registered_at=now - timedelta(days=7),
            check_in_time=now - timedelta(days=5, hours=4),
            emergency_contact='+91 99887 00000 (Father)',
            feedback_rating=5,
            feedback_comment='Incredible drive! Super well-organized segregation counters and warm team spirit.'
        )
        p1.generate_certificate()
        db.session.add(p1)

        p2 = Participation(
            drive_id=drive_completed.id,
            volunteer_id=vol2.id,
            status='attended',
            registered_at=now - timedelta(days=7),
            check_in_time=now - timedelta(days=5, hours=4),
            emergency_contact='+91 91234 00000 (Mother)',
            feedback_rating=5,
            feedback_comment='Learned so much about multi-layer plastic recycling. Proud to contribute!'
        )
        p2.generate_certificate()
        db.session.add(p2)

        # Upcoming participations
        p3 = Participation(
            drive_id=drive1.id,
            volunteer_id=vol1.id,
            status='confirmed',
            registered_at=now - timedelta(days=1),
            emergency_contact='+91 99887 00000'
        )
        db.session.add(p3)

        p4 = Participation(
            drive_id=drive1.id,
            volunteer_id=vol2.id,
            status='registered',
            registered_at=now - timedelta(hours=12),
            emergency_contact='+91 91234 00000'
        )
        db.session.add(p4)

        p5 = Participation(
            drive_id=drive3.id,
            volunteer_id=vol3.id,
            status='confirmed',
            registered_at=now - timedelta(hours=8),
            emergency_contact='+91 98765 00000'
        )
        db.session.add(p5)

        # 8. Notifications
        n1 = Notification(
            user_id=vol1.id,
            title='Drive Registration Confirmed',
            message='You are confirmed for "Mega Girgaon Chowpatty Plastic Interception" on Sunday morning. Check your email for details.',
            notification_type='drive_reminder',
            link='/drives/1'
        )
        n2 = Notification(
            user_id=vol1.id,
            title='Certificate Ready for Download! 🏅',
            message='Congratulations! Your certificate of participation for "Versova Beach Weekend Deep Cleanup" is now available.',
            notification_type='certificate',
            link='/volunteer/registrations'
        )
        n3 = Notification(
            user_id=org1.id,
            title='New Volunteer Registered',
            message='Aarav Sharma and Priya Patel registered for your Girgaon Chowpatty drive.',
            notification_type='drive_update',
            link='/organizer/drives/1/participants'
        )
        db.session.add_all([n1, n2, n3])

        # 9. Messages
        m1 = Message(
            sender_id=vol1.id,
            recipient_id=org1.id,
            drive_id=drive1.id,
            message_text='Hi Ocean Care team! Will you provide gumboots or should volunteers bring our own footwear for the rocky areas?',
            is_read=True
        )
        m2 = Message(
            sender_id=org1.id,
            recipient_id=vol1.id,
            drive_id=drive1.id,
            message_text='Hello Aarav! Sturdy closed sports shoes are perfect for the main sand area. We have heavy-duty puncture-proof nitrile gloves for all attendees!',
            is_read=False
        )
        # Public Q&A on Drive 1
        qa1 = Message(
            sender_id=vol2.id,
            drive_id=drive1.id,
            message_text='Is there safe parking available near the Girgaon Chowpatty meeting canopy?',
            is_public_qa=True,
            answer_text='Yes! Paid municipal parking is available right opposite Mafatlal Swimming Club.',
            answered_at=now - timedelta(hours=10)
        )
        db.session.add_all([m1, m2, qa1])

        db.session.commit()
        print("✅ Database successfully populated with realistic CleanShores sample data!")

if __name__ == '__main__':
    seed()
