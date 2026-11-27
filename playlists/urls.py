from django.urls import path

from . import views

urlpatterns = [
    path('', views.playlist_list_view, name='playlist_list'),
    path('create/', views.playlist_create_view, name='playlist_create'),
    path('<int:playlist_id>/', views.playlist_detail_view, name='playlist_detail'),
    path('<int:playlist_id>/edit/', views.playlist_update_view, name='playlist_update'),
    path('<int:playlist_id>/delete/', views.playlist_delete_view, name='playlist_delete'),
    path('songs/<int:song_id>/add/', views.playlist_add_song_view, name='playlist_add_song'),
    path('<int:playlist_id>/songs/<int:song_id>/action/', views.playlist_song_action_view, name='playlist_song_action'),
]
