"""Add the credited Incompetech sample tracks to the current catalogue."""
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalog.models import Artist, Genre, Song, SongArtist, SongGenre


SAMPLE_ALBUM = 'Incompetech Sample Collection'
SAMPLES = (
    {'title': 'Carefree', 'file': 'Carefree.mp3', 'seconds': 205},
    {'title': 'Monkeys Spinning Monkeys', 'file': 'Monkeys Spinning Monkeys.mp3', 'seconds': 125},
    {'title': 'Sneaky Snitch', 'file': 'Sneaky Snitch.mp3', 'seconds': 137},
    {'title': 'Bittersweet', 'file': 'Bittersweet.mp3', 'seconds': 202},
    {'title': 'Showdown', 'file': 'Showdown.mp3', 'seconds': 73},
)


class Command(BaseCommand):
    help = 'Add the five attributed royalty-free sample recordings without changing existing songs.'

    def handle(self, *args, **options):
        sample_paths = [f'audio/samples/{sample["file"]}' for sample in SAMPLES]
        missing = [path for path in sample_paths if not default_storage.exists(path)]
        if missing:
            raise CommandError(
                'Required credited sample files are missing: ' + ', '.join(missing)
            )

        with transaction.atomic():
            artist, _ = Artist.objects.get_or_create(
                name='Kevin MacLeod',
                defaults={
                    'biography': 'Composer of the sample tracks listed in media/audio/ATTRIBUTION.md.',
                },
            )
            genre, _ = Genre.objects.get_or_create(
                name='Soundtrack',
                defaults={'description': 'Instrumental soundtrack samples used for playback demonstrations.'},
            )
            created = 0
            for sample in SAMPLES:
                file_path = f'audio/samples/{sample["file"]}'
                song, was_created = Song.objects.get_or_create(
                    title=sample['title'],
                    album_name=SAMPLE_ALBUM,
                    defaults={
                        'duration_seconds': sample['seconds'],
                        'audio_file': file_path,
                    },
                )
                if was_created:
                    created += 1
                elif song.audio_file.name not in ('', file_path):
                    raise CommandError(
                        f"Refusing to replace audio already attached to {song.title!r}."
                    )
                elif not song.audio_file.name:
                    song.audio_file = file_path
                    song.duration_seconds = sample['seconds']
                    song.save(update_fields=['audio_file', 'duration_seconds', 'updated_at'])

                SongArtist.objects.get_or_create(
                    song=song, artist=artist, defaults={'role': 'Primary'}
                )
                SongGenre.objects.get_or_create(song=song, genre=genre)

        self.stdout.write(self.style.SUCCESS(
            f'Playback samples ready: {len(SAMPLES)} entries ({created} newly created); '
            'existing catalogue records were left untouched.'
        ))
