"""
Script to capture and save rendered HTML representations of UI views for academic documentation.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.test import Client

def capture_ui():
    client = Client()
    output_dir = BASE_DIR / 'screenshots' / 'ui'
    os.makedirs(output_dir, exist_ok=True)

    # 1. Login view
    res = client.get('/login/')
    with open(output_dir / '01_login_view.html', 'w', encoding='utf-8') as f:
        f.write(res.content.decode('utf-8'))

    # 2. Register view
    res = client.get('/register/')
    with open(output_dir / '02_register_view.html', 'w', encoding='utf-8') as f:
        f.write(res.content.decode('utf-8'))

    # 3. Member Dashboard view
    client.login(username='alex_rhythm', password='MemberDemo2026!')
    res = client.get('/dashboard/')
    with open(output_dir / '03_member_dashboard_view.html', 'w', encoding='utf-8') as f:
        f.write(res.content.decode('utf-8'))

    # 4. Member Profile view
    res = client.get('/profile/')
    with open(output_dir / '04_member_profile_view.html', 'w', encoding='utf-8') as f:
        f.write(res.content.decode('utf-8'))

    client.logout()

    # 5. Admin Dashboard view
    client.login(username='admin_demo', password='AdminDemo2026!')
    res = client.get('/admin-dashboard/')
    with open(output_dir / '05_admin_dashboard_view.html', 'w', encoding='utf-8') as f:
        f.write(res.content.decode('utf-8'))

    # 6. Catalogue Management view
    res = client.get('/catalog/manage/')
    with open(output_dir / '06_catalogue_management_view.html', 'w', encoding='utf-8') as f:
        f.write(res.content.decode('utf-8'))

    client.logout()

    # 7. Access Denied 403 view (when member visits admin dashboard)
    client.login(username='alex_rhythm', password='MemberDemo2026!')
    res = client.get('/admin-dashboard/')
    with open(output_dir / '07_access_denied_view.html', 'w', encoding='utf-8') as f:
        f.write(res.content.decode('utf-8'))

    print("UI snapshots saved successfully in screenshots/ui/")

if __name__ == '__main__':
    capture_ui()
