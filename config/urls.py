"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    # Direct top-level shortcuts for clean URLs
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('register/', accounts_views.register_view, name='register'),
    path('dashboard/', accounts_views.dashboard_view, name='dashboard'),
    path('admin-dashboard/', accounts_views.admin_dashboard_view, name='admin_dashboard'),
    path('profile/', accounts_views.profile_view, name='profile'),
    path('profile/edit/', accounts_views.profile_edit_view, name='profile_edit'),

    # Modular app includes
    path('accounts/', include('accounts.urls')),
    path('catalog/', include('catalog.urls')),
    path('', include('profiles.urls')),
    path('playlists/', include('playlists.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'accounts.views.access_denied_view'
