"""
Management command: remove_unplayable_songs

Removes every catalogue Song whose audio file does not exist on disk.
Songs with valid, non-empty audio files that physically exist inside
MEDIA_ROOT are kept.  Audio files themselves are never deleted.

Usage
-----
Dry run (safe, default):
    python manage.py remove_unplayable_songs

Preview only — prints what would be removed without touching the database.

Apply (destructive):
    python manage.py remove_unplayable_songs --apply

Performs the deletion inside a single database transaction.  If anything
fails, the transaction is rolled back and the database is left unchanged.

What counts as "playable"
--------------------------
A song is considered playable when ALL of the following are true:

1. Its ``audio_file`` field is non-empty.
2. The resolved absolute path is inside ``settings.MEDIA_ROOT``.
3. A regular file exists at that path.
4. The file has a non-zero size.

Cascade behaviour
-----------------
Deleting a Song cascades automatically (via Django FK on_delete=CASCADE) to:
  - catalog_songartist  (SongArtist)
  - catalog_songgenre   (SongGenre)
  - profiles_favourite  (Favourite)
  - playlists_playlistsong (PlaylistSong)

The Song rows themselves are deleted last, inside the same transaction.
No Artist, Genre, Playlist or User records are ever touched.
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Song


class Command(BaseCommand):
    help = (
        "Remove catalogue songs that have no valid audio file. "
        "Runs as a dry run by default; use --apply to commit changes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Perform the deletion. Without this flag the command only prints what would be removed.",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _audio_is_valid(self, song):
        """
        Return True when the song's audio file field points to a regular,
        non-empty file that lives inside MEDIA_ROOT.
        """
        if not song.audio_file or not song.audio_file.name:
            return False

        media_root = os.path.realpath(settings.MEDIA_ROOT)
        try:
            full_path = os.path.realpath(
                os.path.join(media_root, song.audio_file.name)
            )
        except (TypeError, ValueError):
            return False

        # Must be inside MEDIA_ROOT (guard against path traversal)
        if not (full_path.startswith(media_root + os.sep) or full_path == media_root):
            return False

        if not os.path.isfile(full_path):
            return False

        if os.path.getsize(full_path) == 0:
            return False

        return True

    def _count_related(self, songs):
        """Return a dict with cascade counts for a queryset of songs."""
        from catalog.models import SongArtist, SongGenre
        from profiles.models import Favourite
        from playlists.models import PlaylistSong

        pks = list(songs.values_list("pk", flat=True))
        return {
            "song_artists": SongArtist.objects.filter(song_id__in=pks).count(),
            "song_genres":  SongGenre.objects.filter(song_id__in=pks).count(),
            "favourites":   Favourite.objects.filter(song_id__in=pks).count(),
            "playlist_songs": PlaylistSong.objects.filter(song_id__in=pks).count(),
        }

    # ------------------------------------------------------------------
    # Main handler
    # ------------------------------------------------------------------

    def handle(self, *args, **options):
        apply_changes = options["apply"]

        self.stdout.write(self.style.MIGRATE_HEADING("remove_unplayable_songs"))
        self.stdout.write(
            f"  Mode: {'APPLY — deletions will be committed' if apply_changes else 'DRY RUN — no changes will be made'}\n"
        )

        # Classify every song
        all_songs = Song.objects.all().order_by("id")
        total = all_songs.count()

        keep_ids = []
        remove_ids = []

        for song in all_songs:
            if self._audio_is_valid(song):
                keep_ids.append(song.pk)
            else:
                remove_ids.append(song.pk)

        to_keep = Song.objects.filter(pk__in=keep_ids).order_by("id")
        to_remove = Song.objects.filter(pk__in=remove_ids).order_by("id")

        # ---- Report: songs to keep ----
        self.stdout.write(
            self.style.SUCCESS(f"\nSongs with valid audio ({to_keep.count()}) — KEEP:")
        )
        for song in to_keep:
            self.stdout.write(
                f"  ID={song.pk:>3}  {song.title!r:<45}  {song.audio_file.name}"
            )

        # ---- Report: songs to remove ----
        self.stdout.write(
            self.style.WARNING(f"\nSongs without valid audio ({to_remove.count()}) — REMOVE:")
        )
        for song in to_remove:
            reason = "empty audio_file" if not song.audio_file or not song.audio_file.name else "file not found on disk"
            self.stdout.write(
                f"  ID={song.pk:>3}  {song.title!r:<45}  audio='{song.audio_file.name if song.audio_file else ''}'"
                f"  ({reason})"
            )

        # ---- Cascade impact ----
        related = self._count_related(to_remove)
        self.stdout.write(
            self.style.WARNING(
                f"\nRelated records that will cascade:\n"
                f"  SongArtist:   {related['song_artists']}\n"
                f"  SongGenre:    {related['song_genres']}\n"
                f"  Favourite:    {related['favourites']}\n"
                f"  PlaylistSong: {related['playlist_songs']}\n"
                f"  Total:        {sum(related.values())}"
            )
        )

        # ---- Summary before action ----
        self.stdout.write(
            f"\nSummary: {total} total songs → "
            f"{to_keep.count()} to keep, {to_remove.count()} to remove.\n"
        )

        if to_remove.count() == 0:
            self.stdout.write(self.style.SUCCESS("Nothing to remove. Database unchanged."))
            return

        if not apply_changes:
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN complete — no changes made.\n"
                    "Re-run with --apply to perform the deletion."
                )
            )
            return

        # ---- Apply deletion ----
        self.stdout.write(self.style.WARNING("Applying deletion inside a transaction…"))
        try:
            with transaction.atomic():
                deleted_count, breakdown = to_remove.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nDeleted {deleted_count} rows total:\n"
                        + "\n".join(
                            f"  {model}: {count}" for model, count in sorted(breakdown.items())
                        )
                    )
                )
        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"Deletion failed — transaction rolled back.\nError: {exc}")
            )
            raise SystemExit(1)

        # ---- Post-deletion verification ----
        remaining = Song.objects.all()
        self.stdout.write(f"\nPost-deletion song count: {remaining.count()}")
        invalid_remaining = [s for s in remaining if not self._audio_is_valid(s)]
        if invalid_remaining:
            self.stderr.write(
                self.style.ERROR(
                    f"WARNING: {len(invalid_remaining)} song(s) with no valid audio still present after deletion:"
                )
            )
            for s in invalid_remaining:
                self.stderr.write(f"  ID={s.pk}  {s.title!r}")
        else:
            self.stdout.write(
                self.style.SUCCESS("Verification passed: every remaining song has a valid audio file.")
            )
