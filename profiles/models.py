from django.db import models
from django.contrib.auth.models import User


class Favourite(models.Model):
    """
    Associates an authenticated user with their chosen favourite songs.
    Implements a database-level unique constraint to guarantee no duplicate favorites.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
        help_text="Owner of the favourite record."
    )
    song = models.ForeignKey(
        'catalog.Song',
        on_delete=models.CASCADE,
        related_name='favourited_by',
        help_text="Song marked as favourite."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when favourite was registered."
    )

    class Meta:
        verbose_name = 'Favourite'
        verbose_name_plural = 'Favourites'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'song'],
                name='unique_user_song_favourite'
            ),
        ]

    def __str__(self):
        return f"{self.user.username} favourites {self.song.title}"
