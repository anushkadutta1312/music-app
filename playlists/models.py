from django.db import models
from django.contrib.auth.models import User


class Playlist(models.Model):
    """
    User-curated collection of songs.
    Users only possess authorization to modify and manage their own playlists.
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='playlists',
        help_text="User who created and owns this playlist."
    )
    title = models.CharField(
        max_length=150,
        help_text="Title of the playlist."
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the playlist vibe or track theme."
    )
    cover_image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL to custom playlist artwork."
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Whether playlist is visible publicly or private to owner."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when playlist was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when playlist was last modified."
    )

    songs = models.ManyToManyField(
        'catalog.Song',
        through='PlaylistSong',
        related_name='playlists',
        help_text="Songs included in this playlist."
    )

    class Meta:
        verbose_name = 'Playlist'
        verbose_name_plural = 'Playlists'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (by {self.owner.username})"


class PlaylistSong(models.Model):
    """
    Explicit junction table resolving Many-to-Many relationship between Playlist and Song.
    Maintains track order position with database-level positive check constraint.
    """
    playlist = models.ForeignKey(
        Playlist,
        on_delete=models.CASCADE,
        related_name='playlist_songs',
        help_text="Reference to the parent playlist."
    )
    song = models.ForeignKey(
        'catalog.Song',
        on_delete=models.CASCADE,
        related_name='song_playlists',
        help_text="Reference to the included song."
    )
    position = models.PositiveIntegerField(
        default=1,
        help_text="Sequential track ordering position within the playlist (must be >= 1)."
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when track was added to playlist."
    )

    class Meta:
        verbose_name = 'Playlist Song'
        verbose_name_plural = 'Playlist Songs'
        ordering = ['position', 'added_at']
        constraints = [
            models.UniqueConstraint(
                fields=['playlist', 'song'],
                name='unique_playlist_song'
            ),
            models.CheckConstraint(
                condition=models.Q(position__gte=1),
                name='check_playlist_song_position_positive'
            ),
        ]

    def __str__(self):
        return f"#{self.position} {self.song.title} in {self.playlist.title}"
