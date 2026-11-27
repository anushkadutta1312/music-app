from django.urls import path
from . import views

urlpatterns = [
    # Authenticated Member & Admin Browsing
    path('browse/', views.catalogue_browse_view, name='catalogue_browse'),
    path('songs/<int:pk>/', views.song_detail_view, name='song_detail'),
    path('artists/<int:pk>/', views.artist_detail_view, name='artist_detail'),
    path('genres/<int:pk>/', views.genre_detail_view, name='genre_detail'),

    # Admin Management Hub
    path('manage/', views.catalogue_manage_view, name='catalogue_manage'),

    # Admin Song CRUD
    path('manage/songs/', views.song_manage_list_view, name='song_manage_list'),
    path('manage/songs/create/', views.song_create_view, name='song_create'),
    path('manage/songs/<int:pk>/edit/', views.song_update_view, name='song_update'),
    path('manage/songs/<int:pk>/delete/', views.song_delete_view, name='song_delete'),

    # Admin Artist CRUD
    path('manage/artists/', views.artist_manage_list_view, name='artist_manage_list'),
    path('manage/artists/create/', views.artist_create_view, name='artist_create'),
    path('manage/artists/<int:pk>/edit/', views.artist_update_view, name='artist_update'),
    path('manage/artists/<int:pk>/delete/', views.artist_delete_view, name='artist_delete'),

    # Admin Genre CRUD
    path('manage/genres/', views.genre_manage_list_view, name='genre_manage_list'),
    path('manage/genres/create/', views.genre_create_view, name='genre_create'),
    path('manage/genres/<int:pk>/edit/', views.genre_update_view, name='genre_update'),
    path('manage/genres/<int:pk>/delete/', views.genre_delete_view, name='genre_delete'),
]
