"""
Live verification script for authentication endpoints and role-based permissions against db.sqlite3.
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

def verify_live_auth():
    client = Client()

    print("=" * 60)
    print("1. UNAUTHENTICATED ACCESS CHECKS")
    print("=" * 60)
    res_login = client.get('/login/')
    print(f"GET /login/: status {res_login.status_code}")
    assert res_login.status_code == 200

    res_reg = client.get('/register/')
    print(f"GET /register/: status {res_reg.status_code}")
    assert res_reg.status_code == 200

    res_dash_unauth = client.get('/dashboard/')
    print(f"GET /dashboard/ (unauth): status {res_dash_unauth.status_code} -> Redirects to {res_dash_unauth.url}")
    assert res_dash_unauth.status_code == 302

    res_admin_unauth = client.get('/admin-dashboard/')
    print(f"GET /admin-dashboard/ (unauth): status {res_admin_unauth.status_code} -> Redirects to {res_admin_unauth.url}")
    assert res_admin_unauth.status_code == 302

    print("\n" + "=" * 60)
    print("2. MEMBER LOGIN & PERMISSION BOUNDARIES")
    print("=" * 60)
    login_success = client.login(username='alex_rhythm', password='MemberDemo2026!')
    print(f"Member login ('alex_rhythm'): {login_success}")
    assert login_success is True

    res_dash_member = client.get('/dashboard/')
    print(f"GET /dashboard/ as Member: status {res_dash_member.status_code}")
    assert res_dash_member.status_code == 200

    res_profile_member = client.get('/profile/')
    print(f"GET /profile/ as Member: status {res_profile_member.status_code}")
    assert res_profile_member.status_code == 200

    res_admin_by_member = client.get('/admin-dashboard/')
    print(f"GET /admin-dashboard/ as Member (Server Check): status {res_admin_by_member.status_code} (Forbidden)")
    assert res_admin_by_member.status_code == 403

    res_cat_by_member = client.get('/catalog/manage/')
    print(f"GET /catalog/manage/ as Member (Server Check): status {res_cat_by_member.status_code} (Forbidden)")
    assert res_cat_by_member.status_code == 403

    print("\n" + "=" * 60)
    print("3. ADMINISTRATOR LOGIN & PRIVILEGED ACCESS")
    print("=" * 60)
    client.logout()
    admin_login = client.login(username='admin_demo', password='AdminDemo2026!')
    print(f"Admin login ('admin_demo'): {admin_login}")
    assert admin_login is True

    res_dash_admin = client.get('/admin-dashboard/')
    print(f"GET /admin-dashboard/ as Admin: status {res_dash_admin.status_code}")
    assert res_dash_admin.status_code == 200

    res_cat_admin = client.get('/catalog/manage/')
    print(f"GET /catalog/manage/ as Admin: status {res_cat_admin.status_code}")
    assert res_cat_admin.status_code == 200

    print("\n" + "=" * 60)
    print("ALL LIVE ENDPOINT & PERMISSION VERIFICATIONS PASSED!")
    print("=" * 60)

if __name__ == '__main__':
    verify_live_auth()
