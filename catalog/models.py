from django.core.validators import FileExtensionValidator
from django.db import models


class Genre(models.Model):
    """
    Music categorization entity (e.g. Rock, Pop, Jazz, Electronic).
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique name of the music genre."
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the musical style."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when genre was created."
    )

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'
        ordering = ['name']

    def __str__(self):
        return self.name


class Artist(models.Model):
    """
    Musician, band, or creator entity.
    """
    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Name of the artist or band."
    )
    biography = models.TextField(
        blank=True,
        help_text="Artist background and biographical summary."
    )
    image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL to artist promotional photo or avatar."
    )
    external_provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="External music provider name (e.g. YouTube, Jamendo, Spotify)."
    )
    external_artist_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Identifier used on external music platform."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Record creation timestamp."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp."
    )

    class Meta:
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'
        ordering = ['name']

    def __str__(self):
        return self.name


class Song(models.Model):
    """
    Musical track metadata entity.
    Local playback files are optional and reserved for legally reusable samples.
    """
    title = models.CharField(
        max_length=200,
        help_text="Song or track title."
    )
    album_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Album or release collection name."
    )
    duration_seconds = models.PositiveIntegerField(
        help_text="Track duration in seconds. Must be strictly greater than 0."
    )
    release_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Year of original release (must be >= 1900 if supplied)."
    )
    cover_image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL pointing to album or track cover artwork."
    )
    external_provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="External streaming provider (e.g. YouTube, Jamendo)."
    )
    external_track_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="External video or audio stream ID for playback embed."
    )
    audio_file = models.FileField(
        upload_to='audio/tracks/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp3'])],
        help_text="Optional locally hosted MP3 with documented reuse permission."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Record creation timestamp."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp."
    )

    artists = models.ManyToManyField(
        Artist,
        through='SongArtist',
        related_name='songs',
        help_text="Artists associated with this track."
    )
    genres = models.ManyToManyField(
        Genre,
        through='SongGenre',
        related_name='songs',
        help_text="Genres associated with this track."
    )

    class Meta:
        verbose_name = 'Song'
        verbose_name_plural = 'Songs'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(duration_seconds__gt=0),
                name='check_song_duration_positive'
            ),
            models.CheckConstraint(
                condition=models.Q(release_year__gte=1900) | models.Q(release_year__isnull=True),
                name='check_song_release_year_valid'
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def formatted_duration(self):
        """Format duration_seconds into mm:ss format."""
        if not self.duration_seconds:
            return "0:00"
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def audio_url(self):
        """Return a playable URL only when the referenced file exists."""
        if not self.audio_file or not self.audio_file.name:
            return ''
        try:
            if self.audio_file.storage.exists(self.audio_file.name):
                return self.audio_file.url
        except (OSError, ValueError):
            pass
        return ''


class SongArtist(models.Model):
    """
    Explicit junction table resolving Many-to-Many relationship between Song and Artist.
    Supports multi-artist tracks, collaborations, and role designations (e.g. Primary, Featured).
    """
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='song_artists',
        help_text="Reference to the song."
    )
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='artist_songs',
        help_text="Reference to the artist."
    )
    role = models.CharField(
        max_length=50,
        default='Primary',
        help_text="Role of the artist (e.g. Primary, Featured, Producer)."
    )

    class Meta:
        verbose_name = 'Song Artist'
        verbose_name_plural = 'Song Artists'
        constraints = [
            models.UniqueConstraint(
                fields=['song', 'artist'],
                name='unique_song_artist'
            ),
        ]

    def __str__(self):
        return f"{self.song.title} - {self.artist.name} ({self.role})"


class SongGenre(models.Model):
    """
    Explicit junction table resolving Many-to-Many relationship between Song and Genre.
    Enables songs to belong to multiple musical classifications.
    """
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='song_genres',
        help_text="Reference to the song."
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='genre_songs',
        help_text="Reference to the genre."
    )

    class Meta:
        verbose_name = 'Song Genre'
        verbose_name_plural = 'Song Genres'
        constraints = [
            models.UniqueConstraint(
                fields=['song', 'genre'],
                name='unique_song_genre'
            ),
        ]

    def __str__(self):
        return f"{self.song.title} - {self.genre.name}"
