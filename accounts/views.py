from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from .forms import RegistrationForm, LoginForm, ProfileEditForm
from .models import UserProfile
from .decorators import admin_required

from catalog.models import Song, Artist, Genre
from playlists.models import Playlist
from profiles.models import Favourite


def register_view(request):
    """
    User registration view.
    Creates a new user and automatic UserProfile with the MEMBER role.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log in the newly registered user
            login(request, user)
            messages.success(request, f"Welcome to Music App, {user.username}! Your account has been created.")
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    User login view with support for safe 'next' parameter redirection.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")

                    # Verify 'next' URL is safe before redirecting
                    if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                        return redirect(next_url)

                    # Route based on role
                    if hasattr(user, 'profile') and user.profile.role == 'ADMIN':
                        return redirect('admin_dashboard')
                    return redirect('dashboard')
                else:
                    messages.error(request, "This account is inactive. Please contact support.")
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


@require_POST
def logout_view(request):
    """
    User logout view. Accepts POST only to prevent cross-site logout requests.
    Clears session and redirects to home.
    """
    username = request.user.username if request.user.is_authenticated else None
    logout(request)
    if username:
        messages.info(request, f"You have been successfully logged out. See you next time, {username}!")
    return redirect('home')


@login_required
def dashboard_view(request):
    """
    Standard member dashboard.
    Displays user profile summary, playlists, favourites, and quick links.
    """
    user = request.user
    profile = getattr(user, 'profile', None)

    user_playlists = Playlist.objects.filter(owner=user).order_by('-created_at')[:5]
    user_favourites = Favourite.objects.filter(user=user).select_related('song').order_by('-created_at')[:5]
    recent_songs = Song.objects.order_by('-created_at')[:5]

    context = {
        'profile': profile,
        'playlists': user_playlists,
        'favourites': user_favourites,
        'recent_songs': recent_songs,
        'total_playlists': Playlist.objects.filter(owner=user).count(),
        'total_favourites': Favourite.objects.filter(user=user).count(),
    }
    return render(request, 'accounts/dashboard.html', context)


@admin_required
def admin_dashboard_view(request):
    """
    Administrator dashboard.
    Restricted strictly to users with the ADMIN role on the server side.
    Displays catalogue metrics and management options.
    """
    context = {
        'total_users': User.objects.count(),
        'total_artists': Artist.objects.count(),
        'total_genres': Genre.objects.count(),
        'total_songs': Song.objects.count(),
        'total_playlists': Playlist.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:6],
        'recent_songs': Song.objects.order_by('-created_at')[:6],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def profile_view(request):
    """
    View user's own profile and statistics.
    """
    profile = get_object_or_404(UserProfile, user=request.user)
    playlist_count = Playlist.objects.filter(owner=request.user).count()
    favourite_count = Favourite.objects.filter(user=request.user).count()

    context = {
        'profile': profile,
        'playlist_count': playlist_count,
        'favourite_count': favourite_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """
    Edit user's own profile (display name, bio, avatar).
    Users cannot modify their role or administrative privileges.
    """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been successfully updated.")
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form, 'profile': profile})


def access_denied_view(request, exception=None):
    """
    Friendly Access Denied page for HTTP 403 errors.
    Accepts exception parameter for Django handler403 compatibility.
    """
    return render(request, 'accounts/access_denied.html', {'exception': exception}, status=403)
