from django.contrib import admin
from .models import Playlist, PlaylistSong


class PlaylistSongInline(admin.TabularInline):
    model = PlaylistSong
    extra = 1


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_public', 'created_at')
    search_fields = ('title', 'owner__username')
    list_filter = ('is_public',)
    inlines = [PlaylistSongInline]
