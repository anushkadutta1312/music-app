from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponseNotAllowed

from accounts.decorators import admin_required
from profiles.models import Favourite
from playlists.models import Playlist
from .models import Song, Artist, Genre, SongArtist, SongGenre
from .forms import SongForm, ArtistForm, GenreForm, SongFilterForm


# ==============================================================================
# MEMBER & PUBLIC CATALOGUE BROWSING VIEWS (AUTHENTICATED)
# ==============================================================================

@login_required
def catalogue_browse_view(request):
    """
    Catalogue browsing page for both MEMBER and ADMIN users.
    Supports:
    - Search by song title, artist name, and album name.
    - Filter by Genre.
    - Filter by Artist.
    - Combined search and filters.
    - Clean pagination (12 songs/page) with query parameter preservation.
    - Optimized queryset using prefetch_related and select_related to prevent N+1 queries.
    """
    filter_form = SongFilterForm(request.GET or None)

    # Base queryset with prefetched relationships to avoid N+1 queries
    queryset = Song.objects.prefetch_related('artists', 'genres').all()

    q_query = request.GET.get('q', '').strip()
    genre_id = request.GET.get('genre', '').strip()
    artist_id = request.GET.get('artist', '').strip()

    has_active_filters = False

    if q_query:
        queryset = queryset.filter(
            Q(title__icontains=q_query) |
            Q(album_name__icontains=q_query) |
            Q(artists__name__icontains=q_query)
        )
        has_active_filters = True

    if genre_id:
        try:
            genre_pk = int(genre_id)
            queryset = queryset.filter(genres__id=genre_pk)
            has_active_filters = True
        except (ValueError, TypeError):
            pass

    if artist_id:
        try:
            artist_pk = int(artist_id)
            queryset = queryset.filter(artists__id=artist_pk)
            has_active_filters = True
        except (ValueError, TypeError):
            pass

    # Distinct is mandatory when filtering across Many-to-Many relationships to avoid duplicates
    queryset = queryset.distinct().order_by('-created_at', '-id')

    # Pagination: 12 songs per page
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Build querystring without page parameter for pagination links
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    pagination_params = params.urlencode()
    if pagination_params:
        pagination_params = '&' + pagination_params

    context = {
        'page_obj': page_obj,
        'songs': page_obj.object_list,
        'filter_form': filter_form,
        'q_query': q_query,
        'selected_genre_id': genre_id,
        'selected_artist_id': artist_id,
        'has_active_filters': has_active_filters,
        'total_results': paginator.count,
        'pagination_params': pagination_params,
        'genres': Genre.objects.all().order_by('name'),
        'artists': Artist.objects.all().order_by('name'),
        'favourited_song_ids': set(Favourite.objects.filter(
            user=request.user, song__in=page_obj.object_list
        ).values_list('song_id', flat=True)),
    }
    return render(request, 'catalog/browse.html', context)


@login_required
def song_detail_view(request, pk):
    """
    Detailed view of a single song including artists, album, genres, and duration.
    """
    song = get_object_or_404(
        Song.objects.prefetch_related('artists', 'genres'),
        pk=pk
    )
    context = {
        'song': song,
        'song_artists': song.song_artists.select_related('artist').all(),
        'song_genres': song.genres.all(),
        'is_favourited': Favourite.objects.filter(user=request.user, song=song).exists(),
        'owned_playlists': Playlist.objects.filter(owner=request.user).order_by('title'),
    }
    return render(request, 'catalog/song_detail.html', context)


@login_required
def artist_detail_view(request, pk):
    """
    Detailed view of an artist, including biography and catalogue tracks.
    """
    artist = get_object_or_404(Artist, pk=pk)
    songs = artist.songs.prefetch_related('artists', 'genres').distinct().order_by('-created_at')
    context = {
        'artist': artist,
        'songs': songs,
        'song_count': songs.count(),
    }
    return render(request, 'catalog/artist_detail.html', context)


@login_required
def genre_detail_view(request, pk):
    """
    Detailed view of a music genre and associated tracks.
    """
    genre = get_object_or_404(Genre, pk=pk)
    songs = genre.songs.prefetch_related('artists', 'genres').distinct().order_by('-created_at')
    context = {
        'genre': genre,
        'songs': songs,
        'song_count': songs.count(),
    }
    return render(request, 'catalog/genre_detail.html', context)


# ==============================================================================
# ADMINISTRATIVE CATALOGUE MANAGEMENT HUB & CRUD VIEWS (@admin_required)
# ==============================================================================

@admin_required
def catalogue_manage_view(request):
    """
    Administrative catalogue management central hub.
    Strictly protected on the server side by @admin_required.
    """
    context = {
        'songs': Song.objects.prefetch_related('artists').order_by('-created_at')[:8],
        'artists': Artist.objects.annotate(song_count=Count('songs')).order_by('-song_count')[:8],
        'genres': Genre.objects.annotate(song_count=Count('songs')).order_by('name'),
        'total_songs': Song.objects.count(),
        'total_artists': Artist.objects.count(),
        'total_genres': Genre.objects.count(),
    }
    return render(request, 'catalog/manage.html', context)


# ------------------------------------------------------------------------------
# SONG CRUD (Admin Only)
# ------------------------------------------------------------------------------

@admin_required
def song_manage_list_view(request):
    """
    Admin table of all songs with search and management action links.
    """
    q_query = request.GET.get('q', '').strip()
    queryset = Song.objects.prefetch_related('artists', 'genres').all()

    if q_query:
        queryset = queryset.filter(
            Q(title__icontains=q_query) |
            Q(album_name__icontains=q_query) |
            Q(artists__name__icontains=q_query)
        ).distinct()

    queryset = queryset.order_by('-created_at', '-id')
    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    pagination_params = params.urlencode()
    if pagination_params:
        pagination_params = '&' + pagination_params

    context = {
        'page_obj': page_obj,
        'songs': page_obj.object_list,
        'q_query': q_query,
        'total_songs': paginator.count,
        'pagination_params': pagination_params,
    }
    return render(request, 'catalog/manage_songs.html', context)


@admin_required
def song_create_view(request):
    """
    Create a new song with its junction records (SongArtist, SongGenre).
    """
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save()
            messages.success(request, f"Song '{song.title}' was added successfully to the catalogue.")
            return redirect('song_manage_list')
    else:
        form = SongForm()

    context = {
        'form': form,
        'action_title': 'Add New Song',
        'is_edit': False,
    }
    return render(request, 'catalog/song_form.html', context)


@admin_required
def song_update_view(request, pk):
    """
    Update an existing song and synchronize its junction records.
    """
    song = get_object_or_404(Song, pk=pk)

    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES, instance=song)
        if form.is_valid():
            form.save()
            messages.success(request, f"Song '{song.title}' was updated successfully.")
            return redirect('song_manage_list')
    else:
        form = SongForm(instance=song)

    context = {
        'form': form,
        'song': song,
        'action_title': f"Edit Song: {song.title}",
        'is_edit': True,
    }
    return render(request, 'catalog/song_form.html', context)


@admin_required
def song_delete_view(request, pk):
    """
    Delete a song. GET displays confirmation; POST performs deletion.
    """
    song = get_object_or_404(Song, pk=pk)

    if request.method == 'POST':
        title = song.title
        song.delete()
        messages.success(request, f"Song '{title}' was deleted successfully from the catalogue.")
        return redirect('song_manage_list')

    context = {
        'item_type': 'Song',
        'item_name': song.title,
        'cancel_url': 'song_manage_list',
        'impact_details': (
            "Deleting this song will cascade and remove its association with artists, genres, "
            "and any playlist entries or user favourites containing it. "
            "The artists and genres themselves will NOT be deleted."
        ),
    }
    return render(request, 'catalog/confirm_delete.html', context)


# ------------------------------------------------------------------------------
# ARTIST CRUD (Admin Only)
# ------------------------------------------------------------------------------

@admin_required
def artist_manage_list_view(request):
    """
    Admin table of all artists with song counts and management action links.
    """
    q_query = request.GET.get('q', '').strip()
    queryset = Artist.objects.annotate(song_count=Count('songs')).all()

    if q_query:
        queryset = queryset.filter(name__icontains=q_query)

    queryset = queryset.order_by('name')
    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    pagination_params = params.urlencode()
    if pagination_params:
        pagination_params = '&' + pagination_params

    context = {
        'page_obj': page_obj,
        'artists': page_obj.object_list,
        'q_query': q_query,
        'total_artists': paginator.count,
        'pagination_params': pagination_params,
    }
    return render(request, 'catalog/manage_artists.html', context)


@admin_required
def artist_create_view(request):
    """
    Create a new artist.
    """
    if request.method == 'POST':
        form = ArtistForm(request.POST)
        if form.is_valid():
            artist = form.save()
            messages.success(request, f"Artist '{artist.name}' was created successfully.")
            return redirect('artist_manage_list')
    else:
        form = ArtistForm()

    context = {
        'form': form,
        'action_title': 'Add New Artist',
        'is_edit': False,
    }
    return render(request, 'catalog/artist_form.html', context)


@admin_required
def artist_update_view(request, pk):
    """
    Update an existing artist.
    """
    artist = get_object_or_404(Artist, pk=pk)

    if request.method == 'POST':
        form = ArtistForm(request.POST, instance=artist)
        if form.is_valid():
            form.save()
            messages.success(request, f"Artist '{artist.name}' was updated successfully.")
            return redirect('artist_manage_list')
    else:
        form = ArtistForm(instance=artist)

    context = {
        'form': form,
        'artist': artist,
        'action_title': f"Edit Artist: {artist.name}",
        'is_edit': True,
    }
    return render(request, 'catalog/artist_form.html', context)


@admin_required
def artist_delete_view(request, pk):
    """
    Delete an artist. GET displays confirmation; POST performs deletion.
    Cascades to SongArtist junction records; songs themselves remain intact.
    """
    artist = get_object_or_404(Artist, pk=pk)

    if request.method == 'POST':
        name = artist.name
        artist.delete()
        messages.success(request, f"Artist '{name}' was deleted successfully.")
        return redirect('artist_manage_list')

    context = {
        'item_type': 'Artist',
        'item_name': artist.name,
        'cancel_url': 'artist_manage_list',
        'impact_details': (
            f"Deleting this artist will remove artist credit from all linked songs via the "
            f"junction table (SongArtist). The songs themselves will NOT be deleted."
        ),
    }
    return render(request, 'catalog/confirm_delete.html', context)


# ------------------------------------------------------------------------------
# GENRE CRUD (Admin Only)
# ------------------------------------------------------------------------------

@admin_required
def genre_manage_list_view(request):
    """
    Admin table of all genres with song counts and management action links.
    """
    queryset = Genre.objects.annotate(song_count=Count('songs')).order_by('name')
    context = {
        'genres': queryset,
        'total_genres': queryset.count(),
    }
    return render(request, 'catalog/manage_genres.html', context)


@admin_required
def genre_create_view(request):
    """
    Create a new musical genre.
    """
    if request.method == 'POST':
        form = GenreForm(request.POST)
        if form.is_valid():
            genre = form.save()
            messages.success(request, f"Genre '{genre.name}' was created successfully.")
            return redirect('genre_manage_list')
    else:
        form = GenreForm()

    context = {
        'form': form,
        'action_title': 'Add New Genre',
        'is_edit': False,
    }
    return render(request, 'catalog/genre_form.html', context)


@admin_required
def genre_update_view(request, pk):
    """
    Update an existing genre.
    """
    genre = get_object_or_404(Genre, pk=pk)

    if request.method == 'POST':
        form = GenreForm(request.POST, instance=genre)
        if form.is_valid():
            form.save()
            messages.success(request, f"Genre '{genre.name}' was updated successfully.")
            return redirect('genre_manage_list')
    else:
        form = GenreForm(instance=genre)

    context = {
        'form': form,
        'genre': genre,
        'action_title': f"Edit Genre: {genre.name}",
        'is_edit': True,
    }
    return render(request, 'catalog/genre_form.html', context)


@admin_required
def genre_delete_view(request, pk):
    """
    Delete a genre. GET displays confirmation; POST performs deletion.
    Cascades to SongGenre junction records; songs themselves remain intact.
    """
    genre = get_object_or_404(Genre, pk=pk)

    if request.method == 'POST':
        name = genre.name
        genre.delete()
        messages.success(request, f"Genre '{name}' was deleted successfully.")
        return redirect('genre_manage_list')

    context = {
        'item_type': 'Genre',
        'item_name': genre.name,
        'cancel_url': 'genre_manage_list',
        'impact_details': (
            f"Deleting this genre will remove genre classification from linked songs via the "
            f"junction table (SongGenre). The songs themselves will NOT be deleted."
        ),
    }
    return render(request, 'catalog/confirm_delete.html', context)
