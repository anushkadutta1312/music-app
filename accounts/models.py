from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Stores supplementary profile details and role designations for users.
    Extends Django's standard User model via a 1:1 relationship.
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('MEMBER', 'Member'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Reference to the primary Django authentication user."
    )
    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Public-facing display name."
    )
    bio = models.TextField(
        blank=True,
        help_text="Short user biography."
    )
    profile_image = models.URLField(
        max_length=500,
        blank=True,
        help_text="URL pointing to user's profile avatar."
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='MEMBER',
        help_text="Application access level: ADMIN (catalog management) or MEMBER."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when profile was established."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when profile was last altered."
    )

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.display_name or self.user.username} ({self.role})"
