from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and has the ADMIN role.
    Redirects unauthenticated users to login with ?next=...
    Raises PermissionDenied (HTTP 403) for non-admin members.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect(f"/accounts/login/?next={request.path}")

        # Check if user has an associated profile with the ADMIN role or is superuser/staff
        has_admin_role = (
            hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'
        ) or request.user.is_superuser or request.user.is_staff

        if not has_admin_role:
            raise PermissionDenied("Access restricted: Administrator role required.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def member_required(view_func):
    """
    Decorator for views that checks that the user is authenticated.
    Redirects unauthenticated users to login with ?next=...
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access your member dashboard.")
            return redirect(f"/accounts/login/?next={request.path}")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
