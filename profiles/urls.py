from django.urls import path

from . import views

urlpatterns = [
    path('favourites/', views.favourites_list_view, name='my_favourites'),
    path('favourites/<int:song_id>/', views.favourite_action_view, name='favourite_action'),
]
