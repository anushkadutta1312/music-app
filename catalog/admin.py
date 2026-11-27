from django.contrib import admin
from .models import Song, Artist, Genre, SongArtist, SongGenre


class SongArtistInline(admin.TabularInline):
    model = SongArtist
    extra = 1


class SongGenreInline(admin.TabularInline):
    model = SongGenre
    extra = 1


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'album_name', 'duration_seconds', 'release_year', 'has_audio', 'created_at')
    search_fields = ('title', 'album_name', 'artists__name')
    list_filter = ('release_year', 'genres')
    inlines = [SongArtistInline, SongGenreInline]
    fields = (
        'title',
        'album_name',
        'duration_seconds',
        'release_year',
        'cover_image_url',
        'audio_file',
        'external_provider',
        'external_track_id',
    )

    def has_audio(self, obj):
        return bool(obj.audio_file)
    has_audio.boolean = True
    has_audio.short_description = "Audio Uploaded"


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'external_provider', 'created_at')
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
