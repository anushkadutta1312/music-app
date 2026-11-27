from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from catalog.models import Song
from .models import Favourite


def _wants_json(request):
    return 'application/json' in request.headers.get('Accept', '').lower()


@login_required
def favourites_list_view(request):
    """Show only the signed-in user's saved songs."""
    favourites = (
        Favourite.objects.filter(user=request.user)
        .select_related('song')
        .prefetch_related('song__artists', 'song__genres')
    )
    return render(request, 'profiles/favourites.html', {'favourites': favourites})


@login_required
@require_POST
def favourite_action_view(request, song_id):
    """Add or remove a favourite owned by the current user only."""
    action = request.POST.get('action')
    if action not in {'add', 'remove'}:
        if _wants_json(request):
            return JsonResponse({'success': False, 'error': 'Choose add or remove.'}, status=400)
        messages.error(request, 'That favourite action is not valid.')
        return redirect('my_favourites')

    try:
        song = Song.objects.get(pk=song_id)
    except Song.DoesNotExist:
        if _wants_json(request):
            return JsonResponse({'success': False, 'error': 'Song not found.'}, status=404)
        raise Http404('Song not found.')
    favourite_query = Favourite.objects.filter(user=request.user, song=song)
    if action == 'add':
        _, created = Favourite.objects.get_or_create(user=request.user, song=song)
        is_favourited = True
        message = 'Song added to your favourites.' if created else 'Song is already in your favourites.'
    else:
        favourite_query.delete()
        is_favourited = False
        message = 'Song removed from your favourites.'

    if _wants_json(request):
        return JsonResponse({
            'success': True,
            'song_id': song.pk,
            'is_favourited': is_favourited,
            'message': message,
        })

    messages.success(request, message)
    referer = request.META.get('HTTP_REFERER', '')
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
        return redirect(referer)
    return redirect('my_favourites')
