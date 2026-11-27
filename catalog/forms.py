from django import forms
from django.db import transaction
from .models import Song, Artist, Genre, SongArtist, SongGenre


class SongForm(forms.ModelForm):
    """
    Form for creating and editing Songs with explicit Many-to-Many
    junction management (SongArtist and SongGenre).
    """
    artists = forms.ModelMultipleChoiceField(
        queryset=Artist.objects.all().order_by('name'),
        required=True,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '5',
        }),
        help_text="Hold Ctrl (or Cmd) to select multiple artists."
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all().order_by('name'),
        required=True,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '5',
        }),
        help_text="Hold Ctrl (or Cmd) to select multiple genres."
    )

    class Meta:
        model = Song
        fields = [
            'title',
            'album_name',
            'duration_seconds',
            'release_year',
            'cover_image_url',
            'external_provider',
            'external_track_id',
            'audio_file',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Song title'}),
            'album_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Album name (optional)'}),
            'duration_seconds': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration in seconds (e.g. 215)', 'min': '1'}),
            'release_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024', 'min': '1900'}),
            'cover_image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'external_provider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. YouTube, Jamendo, Spotify'}),
            'external_track_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. dQw4w9WgXcQ'}),
            'audio_file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.mp3,audio/mpeg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['artists'].initial = self.instance.artists.all()
            self.fields['genres'].initial = self.instance.genres.all()

    def clean_duration_seconds(self):
        duration = self.cleaned_data.get('duration_seconds')
        if duration is None or duration <= 0:
            raise forms.ValidationError("Duration must be strictly greater than 0 seconds.")
        return duration

    def clean_release_year(self):
        year = self.cleaned_data.get('release_year')
        if year is not None and year < 1900:
            raise forms.ValidationError("Release year must be 1900 or later.")
        return year

    def save(self, commit=True):
        if not commit:
            return super().save(commit=False)

        # Keep the song row and both explicit junction tables in one unit of
        # work. If syncing either relationship fails, the song edit/create is
        # rolled back along with any junction changes.
        with transaction.atomic():
            instance = super().save(commit=True)
            self._save_junctions(instance)
        return instance

    def save_m2m(self):
        self._save_junctions(self.instance)

    def _save_junctions(self, song):
        selected_artists = list(self.cleaned_data.get('artists', []))
        selected_genres = list(self.cleaned_data.get('genres', []))

        with transaction.atomic():
            # Synchronize SongArtist junction
            existing_artist_ids = set(
                SongArtist.objects.filter(song=song).values_list('artist_id', flat=True)
            )
            selected_artist_ids = {a.id for a in selected_artists}

            # Remove unselected
            to_remove_artists = existing_artist_ids - selected_artist_ids
            if to_remove_artists:
                SongArtist.objects.filter(song=song, artist_id__in=to_remove_artists).delete()

            # Add newly selected
            to_add_artists = selected_artist_ids - existing_artist_ids
            for artist_id in to_add_artists:
                SongArtist.objects.create(
                    song=song,
                    artist_id=artist_id,
                    role='Primary'
                )

            # Synchronize SongGenre junction
            existing_genre_ids = set(
                SongGenre.objects.filter(song=song).values_list('genre_id', flat=True)
            )
            selected_genre_ids = {g.id for g in selected_genres}

            # Remove unselected
            to_remove_genres = existing_genre_ids - selected_genre_ids
            if to_remove_genres:
                SongGenre.objects.filter(song=song, genre_id__in=to_remove_genres).delete()

            # Add newly selected
            to_add_genres = selected_genre_ids - existing_genre_ids
            for genre_id in to_add_genres:
                SongGenre.objects.create(
                    song=song,
                    genre_id=genre_id
                )


class ArtistForm(forms.ModelForm):
    """
    Form for creating and editing Artists.
    """
    class Meta:
        model = Artist
        fields = [
            'name',
            'biography',
            'image_url',
            'external_provider',
            'external_artist_id',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Artist or band name'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Artist biography and notes...'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'external_provider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. YouTube, Spotify'}),
            'external_artist_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'External artist identifier'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Artist name is required.")
        return name


class GenreForm(forms.ModelForm):
    """
    Form for creating and editing Genres.
    """
    class Meta:
        model = Genre
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Synthwave, Indie Rock, Jazz'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Genre description and stylistic origins...'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Genre name is required.")
        return name


class SongFilterForm(forms.Form):
    """
    Search and filter form for the catalogue browse view.
    """
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, artist, or album...',
        })
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all().order_by('name'),
        required=False,
        empty_label="All Genres",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    artist = forms.ModelChoiceField(
        queryset=Artist.objects.all().order_by('name'),
        required=False,
        empty_label="All Artists",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
