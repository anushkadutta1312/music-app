# Authentication, User Roles & Server-Side Permissions

This document details the authentication architecture, user roles, security model, and server-side authorization mechanisms implemented in the **Music App**.

---

## 1. Authentication Architecture Overview

The **Music App** leverages Django's battle-tested built-in authentication system (`django.contrib.auth`), adhering strictly to security best practices:
- **Password Hashing**: Passwords are never stored in plain text. Django hashes all passwords using **PBKDF2 with a SHA-256 hash** and a unique per-user salt.
- **Session Management**: Authenticated state is maintained via cryptographically signed HTTP cookies containing session identifiers (`django_session`), rather than storing credentials on the client.
- **CSRF Protection**: All state-modifying requests (Registration, Login, Profile Edit, Logout) require a valid CSRF token (`{% csrf_token %}`) enforced by `CsrfViewMiddleware`.
- **Safe Redirection**: Redirection via the `?next=...` query parameter validates that the target URL belongs to the allowed host using `django.utils.http.url_has_allowed_host_and_scheme`, preventing open-redirect attacks.

---

## 2. Difference Between `User` and `UserProfile`

To maintain clean separation of concerns and avoid monkey-patching core authentication logic, the system utilizes a **One-to-One (1:1)** architecture:

```
+------------------------------------+          +------------------------------------+
|         auth_user (Django)         |          |        accounts_userprofile        |
+------------------------------------+          +------------------------------------+
| id (PK)                            | 1      1 | id (PK)                            |
| username (UNIQUE)                  |<-------->| user_id (FK, UNIQUE, CASCADE)      |
| email                              |          | display_name                       |
| password (PBKDF2 Hash)             |          | bio                                |
| is_staff / is_superuser            |          | profile_image                      |
| date_joined                        |          | role ('ADMIN' | 'MEMBER')          |
+------------------------------------+          +------------------------------------+
```

### Why This Separation Matters:
1. **Security Isolation**: Core authentication fields (`password`, `is_staff`, `is_superuser`, `last_login`) reside securely in `auth_user`. Application-specific metadata (`display_name`, `bio`, `profile_image`, `role`) resides in `accounts_userprofile`.
2. **Cascading Lifecycles**: If a user account is deleted, the corresponding profile is automatically removed (`on_delete=models.CASCADE`).
3. **Privilege Separation**: Ordinary member forms edit only `UserProfile` fields, strictly excluding authentication flags and the `role` field.

---

## 3. Application Roles & Permissions Matrix

The platform enforces two distinct application roles:
- **`ADMIN`** (Catalogue Management & System Oversight)
- **`MEMBER`** (Music Discovery, Playlists, and Favourites)

| Capability / Feature Endpoint | Anonymous Guest | Authenticated `MEMBER` | Authenticated `ADMIN` | Enforcement Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **Public Landing Page** (`/`) | Allowed | Allowed | Allowed | Public TemplateView |
| **User Registration** (`/register/`) | Allowed | Redirects to Dashboard | Redirects to Dashboard | View-level redirect |
| **User Login** (`/login/`) | Allowed | Redirects to Dashboard | Redirects to Dashboard | View-level redirect |
| **User Logout** (`/logout/`) | Redirects | Allowed (POST only) | Allowed (POST only) | `@require_POST`, CSRF middleware, clears session |
| **Member Dashboard** (`/dashboard/`) | Denied (302 Login) | **Allowed** | **Allowed** | `@login_required` |
| **View Profile** (`/profile/`) | Denied (302 Login) | **Allowed** (Own only) | **Allowed** (Own only) | `@login_required` & `request.user` |
| **Edit Profile** (`/profile/edit/`) | Denied (302 Login) | **Allowed** (Own only) | **Allowed** (Own only) | `@login_required` & Form Isolation |
| **Admin Dashboard** (`/admin-dashboard/`)| Denied (302 Login) | **Denied (403 Forbidden)**| **Allowed** | **`@admin_required`** |
| **Catalogue Management** (`/catalog/manage/`)| Denied (302 Login) | **Denied (403 Forbidden)**| **Allowed** | **`@admin_required`** |
| **Django Admin Site** (`/admin/`) | Denied (302 Login) | **Denied (Staff only)** | **Allowed** (`is_staff=True`)| Django Admin auth |

---

## 4. Server-Side Authorization Implementation

Relying solely on frontend UI hiding (e.g. `{% if user.is_staff %}`) is insecure. This application implements **multi-layered server-side verification**:

### 4.1 Reusable Decorator: `@admin_required`
Located in [accounts/decorators.py](file:///c:/Users/Hp/Desktop/MY%20PROJECT/accounts/decorators.py):
```python
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect(f"/accounts/login/?next={request.path}")

        has_admin_role = (
            hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'
        ) or request.user.is_superuser or request.user.is_staff

        if not has_admin_role:
            raise PermissionDenied("Access restricted: Administrator role required.")

        return view_func(request, *args, **kwargs)
    return _wrapped_view
```
- If an unauthenticated visitor requests `/admin-dashboard/`, they are redirected to `/login/?next=/admin-dashboard/`.
- If an authenticated `MEMBER` requests `/admin-dashboard/` or `/catalog/manage/`, the server immediately raises `PermissionDenied`, serving an HTTP **403 Forbidden** page.

### 4.2 Form-Level Privilege Escalation Protection
In [accounts/forms.py](file:///c:/Users/Hp/Desktop/MY%20PROJECT/accounts/forms.py):
1. **Registration**:
   ```python
   # RegistrationForm.save() strictly hardcodes:
   UserProfile.objects.create(user=user, display_name=username, role='MEMBER')
   ```
   Users cannot submit a role in the registration payload.
2. **Profile Edit**:
   ```python
   class ProfileEditForm(forms.ModelForm):
       class Meta:
           model = UserProfile
           fields = ['display_name', 'bio', 'profile_image']  # 'role' is strictly excluded!
   ```
   If a malicious member attempts to tamper with the HTTP POST payload by adding `role=ADMIN`, Django's Form processing discards the unexpected field, leaving the user's role unchanged as `MEMBER`.

---

## 5. Development Demo Credentials

The `seed_data` command creates synthetic administrator and member accounts for local evaluation. Its development passwords are intentionally fixed for repeatable tests; do not deploy these seeded accounts or their passwords publicly. The login page does not display these credentials. For a public deployment, create new accounts with unique passwords and do not run the sample seed command.

---

## 6. How to Test and Verify Both Roles

### Test 1: Member Flow
1. Open [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/).
2. Log in with a locally provisioned MEMBER account.
3. Notice that you are redirected to the **Member Dashboard** (`/dashboard/`).
4. Notice the navigation bar shows: *Home, Dashboard, My Profile, Logout*.
5. Manually type `http://127.0.0.1:8000/admin-dashboard/` into your browser address bar.
6. **Result**: The server denies access with an **HTTP 403 Forbidden / Access Denied** page.

### Test 2: Administrator Flow
1. Click **Logout**.
2. Log in with a locally provisioned ADMIN account.
3. Notice the navigation bar dynamically displays: *Home, Dashboard, Admin Dashboard, Catalogue Management, My Profile, Logout*.
4. Navigate to **Admin Dashboard** (`/admin-dashboard/`).
5. **Result**: The server authorizes the request and renders system-wide metrics.
