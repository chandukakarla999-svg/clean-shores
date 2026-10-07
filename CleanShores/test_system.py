import unittest
import os
import io
from datetime import datetime, timedelta

# Ensure isolated test database for unit testing
test_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_runner.db'))
os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'

from app import create_app
from models import db, User, Drive, OrganizerVerification, Participation

class CleanShoresComprehensiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.drop_all()
            db.create_all()
            from seed_db import seed
            seed()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except Exception:
                pass



    def test_01_public_frontend_pages(self):
        """Test public landing and information pages render with 200 OK"""
        print("\n[TEST 1] Testing public frontend pages...")
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'CleanShores', res.data)

        res = self.client.get('/about')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/drives')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/volunteer')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Volunteer Portal', res.data)

        res = self.client.get('/organizer')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Create Account', res.data)
        self.assertIn(b'Sign In', res.data)
        print("  --> Public pages passed (200 OK)!")

    def test_02_organizer_registration_and_immediate_signin(self):
        """Test that registering an organizer does NOT ask for verification and logs in directly"""
        print("\n[TEST 2] Testing Organizer registration and immediate sign in (no verification asked)...")
        timestamp = int(datetime.utcnow().timestamp())
        username = f"org_test_{timestamp}"
        email = f"test_{timestamp}@ecoprotect.org"
        
        post_data = {
            'action': 'register',
            'college_or_org': 'EcoProtect Wildlife Initiative',
            'full_name': 'Test Org Leader',
            'username': username,
            'email': email,
            'phone': '+91 98989 12345',
            'location': 'Mumbai, Maharashtra',
            'password': 'TestPassword123!',
            'confirm_password': 'TestPassword123!'
        }
        
        res = self.client.post('/organizer', data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        # Verify redirect landed on Organizer Dashboard
        self.assertIn(b'Dashboard', res.data)
        self.assertIn(b'New Drive', res.data)
        # Ensure NO 'Verification Required' banner is shown
        self.assertNotIn(b'Verification Required', res.data)
        self.assertNotIn(b'Submit your documents to get started', res.data)

        # Check in DB that user is marked verified
        with self.app.app_context():
            user = User.query.filter_by(username=username).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.role, 'organizer')
            self.assertTrue(user.is_verified)
            self.assertEqual(user.verification_status, 'verified')
        print("  --> Organizer created account, signed in immediately, verified by default!")

    def test_03_organizer_create_drive_without_verification_block(self):
        """Test organizer can immediately create a cleanup drive without being blocked"""
        print("\n[TEST 3] Testing Organizer creating drive immediately...")
        # Login as the demo organizer
        login_data = {
            'action': 'login',
            'identifier': 'organizer@cleanshores.org',
            'password': 'Demo@2026!'
        }
        res = self.client.post('/organizer', data=login_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dashboard', res.data)
        # Verify "New Drive" button is present and NO warning banner
        self.assertIn(b'New Drive', res.data)
        self.assertNotIn(b'Verification Required', res.data)

        # Access create-drive page
        res = self.client.get('/organizer/create-drive')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Create Cleanup Drive', res.data)

        # Submit a new drive
        now = datetime.utcnow() + timedelta(days=5)
        end = now + timedelta(hours=3)
        drive_data = {
            'title': f'Automated Test Coastal Cleanup {int(now.timestamp())}',
            'category': 'Beach Cleanup',
            'description': 'Community beach plastic removal testing drive.',
            'location_name': 'Juhu Beach Section 4',
            'address': 'Juhu Tara Road',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'meeting_point': 'Near Shivaji Statue',
            'start_datetime': now.strftime('%Y-%m-%dT%H:%M'),
            'end_datetime': end.strftime('%Y-%m-%dT%H:%M'),
            'max_volunteers': 60,
            'supplies_provided': 'Bags, Gloves, Sanitizers',
            'supplies_needed': 'Reusable Water Bottles',
            'safety_guidelines': 'Wear sturdy footwear and sun protection.',
            'waste_segregation_plan': 'Separate plastic bottles, nets, and organic debris.'
        }
        res = self.client.post('/organizer/create-drive', data=drive_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'created successfully', res.data)
        print("  --> Organizer created drive successfully without any verification obstruction!")

    def test_04_volunteer_registration_and_drive_join(self):
        """Test volunteer registration, sign in, and joining a drive"""
        print("\n[TEST 4] Testing Volunteer registration and joining drive...")
        timestamp = int(datetime.utcnow().timestamp())
        username = f"vol_test_{timestamp}"
        email = f"vol_{timestamp}@student.org"
        
        post_data = {
            'action': 'register',
            'full_name': 'Aanya Sengupta',
            'username': username,
            'email': email,
            'phone': '+91 99000 88776',
            'location': 'Mumbai',
            'college_or_org': 'St. Xavier Eco Forum',
            'password': 'VolunteerPass123!',
            'confirm_password': 'VolunteerPass123!'
        }
        res = self.client.post('/volunteer', data=post_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dashboard', res.data)

        # Find an upcoming drive to join
        with self.app.app_context():
            drive = Drive.query.filter_by(status='upcoming').first()
            drive_id = drive.id

        res = self.client.post(f'/drives/{drive_id}/register', follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        print("  --> Volunteer registered, signed in, and joined drive successfully!")

    def test_05_admin_login_and_dashboards(self):
        """Test admin login and admin management pages"""
        print("\n[TEST 5] Testing Admin portal...")
        # Logout current user first
        self.client.get('/logout')

        login_data = {
            'role': '',
            'identifier': 'admin@cleanshores.org',
            'password': 'Admin@2026!'
        }
        res = self.client.post('/login', data=login_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Admin', res.data)

        # Admin subpages
        for endpoint in ['/admin/dashboard', '/admin/organizers', '/admin/drives', '/admin/users']:
            res = self.client.get(endpoint)
            self.assertEqual(res.status_code, 200)
        print("  --> Admin dashboard and sections passed (200 OK)!")

    def test_06_error_handling(self):
        """Test 404 custom error handler"""
        print("\n[TEST 6] Testing Error handlers...")
        res = self.client.get('/nonexistent-page-url-404')
        self.assertEqual(res.status_code, 404)
        print("  --> Custom 404 handled properly!")

if __name__ == '__main__':
    unittest.main()
