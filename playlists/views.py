from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Max
from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from catalog.models import Song
from .forms import PlaylistForm
from .models import Playlist, PlaylistSong


def _wants_json(request):
    return 'application/json' in request.headers.get('Accept', '').lower()


def _json_error(request, message, status):
    if _wants_json(request):
        return JsonResponse({'success': False, 'error': message}, status=status)
    messages.error(request, message)
    return None


def _owned_playlist_or_404(request, playlist_id):
    return get_object_or_404(Playlist, pk=playlist_id, owner=request.user)


def _ordered_tracks(playlist):
    return list(
        PlaylistSong.objects.filter(playlist=playlist)
        .select_related('song')
        .prefetch_related('song__artists', 'song__genres')
        .order_by('position', 'added_at', 'id')
    )


def _save_track_order(tracks):
    """Write a contiguous, one-based order to the existing position field."""
    for position, track in enumerate(tracks, start=1):
        track.position = position
    if tracks:
        PlaylistSong.objects.bulk_update(tracks, ['position'])


@login_required
def playlist_list_view(request):
    playlists = (
        Playlist.objects.filter(owner=request.user)
        .annotate(song_count=Count('playlist_songs'))
        .order_by('-created_at', '-id')
    )
    return render(request, 'playlists/list.html', {'playlists': playlists})


@login_required
def playlist_create_view(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.owner = request.user
            playlist.is_public = False
            playlist.save()
            messages.success(request, f"Playlist '{playlist.title}' was created.")
            return redirect('playlist_detail', playlist_id=playlist.pk)
    else:
        form = PlaylistForm()
    return render(request, 'playlists/form.html', {
        'form': form,
        'page_title': 'Create Playlist',
        'submit_label': 'Create Playlist',
    })


@login_required
def playlist_detail_view(request, playlist_id):
    playlist = _owned_playlist_or_404(request, playlist_id)
    tracks = _ordered_tracks(playlist)
    return render(request, 'playlists/detail.html', {
        'playlist': playlist,
        'tracks': tracks,
        'song_count': len(tracks),
        'playable_count': sum(1 for track in tracks if track.song.audio_url),
    })


@login_required
def playlist_update_view(request, playlist_id):
    playlist = _owned_playlist_or_404(request, playlist_id)
    if request.method == 'POST':
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            form.save()
            messages.success(request, f"Playlist '{playlist.title}' was updated.")
            return redirect('playlist_detail', playlist_id=playlist.pk)
    else:
        form = PlaylistForm(instance=playlist)
    return render(request, 'playlists/form.html', {
        'form': form,
        'playlist': playlist,
        'page_title': 'Edit Playlist',
        'submit_label': 'Save Changes',
    })


@login_required
@require_http_methods(['GET', 'POST'])
def playlist_delete_view(request, playlist_id):
    playlist = _owned_playlist_or_404(request, playlist_id)
    if request.method == 'POST':
        title = playlist.title
        playlist.delete()
        messages.success(request, f"Playlist '{title}' was deleted.")
        return redirect('playlist_list')
    return render(request, 'playlists/confirm_delete.html', {'playlist': playlist})


@login_required
def playlist_add_song_view(request, song_id):
    if request.method == 'GET' and 'playlist_id' in request.GET:
        return HttpResponseNotAllowed(['POST'])

    try:
        song = Song.objects.get(pk=song_id)
    except Song.DoesNotExist:
        if _wants_json(request):
            return JsonResponse({'success': False, 'error': 'Song not found.'}, status=404)
        raise Http404('Song not found.')

    if request.method == 'GET':
        user_playlists = Playlist.objects.filter(owner=request.user).order_by('-updated_at')
        existing_playlist_ids = set(
            PlaylistSong.objects.filter(playlist__in=user_playlists, song=song)
            .values_list('playlist_id', flat=True)
        )
        return render(request, 'playlists/add_song.html', {
            'song': song,
            'user_playlists': user_playlists,
            'existing_playlist_ids': existing_playlist_ids,
        })

    playlist_id = request.POST.get('playlist_id', '').strip()
    try:
        playlist_id = int(playlist_id)
    except (TypeError, ValueError):
        response = _json_error(request, 'Choose one of your playlists.', 400)
        return response or redirect('playlist_list')

    try:
        playlist = Playlist.objects.get(pk=playlist_id, owner=request.user)
    except Playlist.DoesNotExist:
        response = _json_error(request, 'Playlist not found.', 404)
        return response or redirect('playlist_list')

    with transaction.atomic():
        tracks = list(
            PlaylistSong.objects.filter(playlist=playlist)
            .order_by('position', 'added_at', 'id')
        )
        _save_track_order(tracks)
        maximum = PlaylistSong.objects.filter(playlist=playlist).aggregate(value=Max('position'))['value'] or 0
        _, created = PlaylistSong.objects.get_or_create(
            playlist=playlist,
            song=song,
            defaults={'position': maximum + 1},
        )

    message = 'Song added to the playlist.' if created else 'That song is already in the playlist.'
    if _wants_json(request):
        return JsonResponse({
            'success': True,
            'created': created,
            'playlist_id': playlist.pk,
            'song_id': song.pk,
            'message': message,
        })
    messages.success(request, message)
    return redirect('playlist_detail', playlist_id=playlist.pk)


@login_required
@require_POST
def playlist_song_action_view(request, playlist_id, song_id):
    action = request.POST.get('action', '')
    if action not in {'remove', 'move_up', 'move_down'}:
        response = _json_error(request, 'Choose a valid playlist song action.', 400)
        return response or redirect('playlist_list')

    try:
        playlist = Playlist.objects.get(pk=playlist_id, owner=request.user)
    except Playlist.DoesNotExist:
        response = _json_error(request, 'Playlist not found.', 404)
        return response or redirect('playlist_list')

    try:
        with transaction.atomic():
            tracks = _ordered_tracks(playlist)
            track_index = next(index for index, item in enumerate(tracks) if item.song_id == song_id)
            track = tracks[track_index]

            if action == 'remove':
                track.delete()
                tracks.pop(track_index)
                _save_track_order(tracks)
                message = 'Song removed from the playlist.'
            else:
                target_index = track_index - 1 if action == 'move_up' else track_index + 1
                if target_index < 0 or target_index >= len(tracks):
                    message = 'That song is already at the edge of the playlist.'
                else:
                    tracks[track_index], tracks[target_index] = tracks[target_index], tracks[track_index]
                    _save_track_order(tracks)
                    message = 'Playlist order updated.'
    except StopIteration:
        response = _json_error(request, 'Song is not in this playlist.', 404)
        return response or redirect('playlist_detail', playlist_id=playlist_id)

    if _wants_json(request):
        return JsonResponse({
            'success': True,
            'action': action,
            'song_id': song_id,
            'message': message,
            'positions': [
                {'song_id': item.song_id, 'position': item.position}
                for item in _ordered_tracks(playlist)
            ],
        })
    messages.success(request, message)
    return redirect('playlist_detail', playlist_id=playlist.pk)
