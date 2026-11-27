# Phase 9 — Favourites Management Report

**Status:** Complete and verified.

## Architecture

The implementation reuses `profiles.Favourite` and the existing `profiles_favourite` table. Its existing unique constraint on `(user, song)` remains the duplicate safeguard; no model edits, schema changes, or migrations were made.

`profiles/urls.py` adds:

- `my_favourites` at `/favourites/` for the signed-in user's list.
- `favourite_action` at `/favourites/<song_id>/` for POST-only add/remove actions.

The `@login_required` view obtains the owner from `request.user`; the action accepts no owner identifier. It uses `get_or_create` for adds and deletes only a matching `(request.user, song)` row for removals. Song lookup validates the requested ID. JSON callers receive success, current favourite state, and feedback text; invalid actions return 400 and unknown song IDs return 404. Standard form submissions receive a message and a same-site referer redirect (or the favourites page as a fallback).

`templates/profiles/favourites.html` shows each user's own songs with title, artist, genre, duration, album/year metadata, detail links, and a useful empty state. The shared `_favourite_button.html` provides a CSRF-protected POST form as the no-JavaScript fallback. The catalogue browse and song detail views provide favourite state for the current user, and `templates/base.html` links to My Favourites for authenticated users.

`static/js/favourites.js` intercepts the form submission and sends `FormData` with `Accept: application/json`, same-origin credentials, and the CSRF header. On success it updates button label, state, and feedback without a page reload. On the favourites page it removes the card from the rendered list and displays the empty state when the last item is removed. Errors are announced inline, and the original POST form remains functional when JavaScript is unavailable.

## Authorization and safety

- Anonymous requests to protected pages/actions redirect to login.
- MEMBER and ADMIN accounts can manage their own favourites.
- The URL identifies only a song; ownership always comes from the authenticated session.
- Attempts to supply another user's ID do not affect that user's records.
- Mutation is POST-only and Django CSRF middleware remains active.
- Removing a favourite does not delete its song.

## Automated tests

Created `profiles/tests_views.py` with 14 tests covering both user roles, successful add, duplicate add, remove/song preservation, owner-isolated list data, empty state, anonymous restrictions, MEMBER and ADMIN isolation, invalid action/song IDs, conventional form fallback, GET rejection, CSRF rejection/acceptance, and current-user state on browse and detail pages.

Final verification:

- `python manage.py check`: **passed**, no issues.
- `python manage.py test profiles.tests_views --verbosity=2`: **14 tests passed**.
- `python manage.py test --verbosity=2`: **90 tests passed in 127.734 seconds**; Django reported no system-check issues.

The test suite used Django's in-memory test database; the existing populated `db.sqlite3` was not reset.

## Browser verification

Used the running local application with the existing ADMIN and MEMBER demo accounts, and `kevin_newbie` (the existing empty-favourites account) for the empty-state view.

- ADMIN added a song with Fetch, saw success feedback and the updated button, removed it, and opened the populated My Favourites page.
- MEMBER added multiple songs, opened My Favourites, and removed a song directly from that page without a reload.
- After MEMBER removed a song also favourited by ADMIN, ADMIN's favourite remained present.
- The empty page, favourited and non-favourited button states, and successful asynchronous response were captured.
- A browser-discovered JavaScript issue was fixed: the hidden field named `action` shadows `HTMLFormElement.action`; Fetch now reads the endpoint with `form.getAttribute('action')`.

Genuine browser captures (JPEG data saved with `.jpg` extensions) are in `screenshots/ui/`:

- `phase9_01_favourites_with_songs_admin.jpg`
- `phase9_02_favourites_with_songs_member.jpg`
- `phase9_03_song_nonfavourited.jpg`
- `phase9_04_song_favourited.jpg`
- `phase9_05_fetch_success.jpg`
- `phase9_06_empty_favourites.jpg`

## Database integrity

After browser verification and the full automated suite, the existing database contained 12 users, 12 profiles, 55 songs, 20 artists, 10 genres, 59 song-artist links, 94 song-genre links, 54 favourites, 15 playlists, and 70 playlist-song links. These match the previously verified sample-data counts. ADMIN and MEMBER demo-account favourite counts also returned to their pre-walkthrough values after removing the temporary favourite records created for browser checks.

SQLite `integrity_check` returned `ok`; `foreign_key_check` returned no violations. No migration file was generated, and the project database schema was not changed. Django used its existing migrations only to prepare the in-memory test database.

## Files created or modified

- Created: `profiles/urls.py`
- Created: `profiles/tests_views.py`
- Created: `templates/profiles/favourites.html`
- Created: `templates/profiles/_favourite_button.html`
- Created: `static/js/favourites.js`
- Created: six screenshots listed above
- Created: `docs/PHASE_9_FAVOURITES_REPORT.md`
- Modified: `profiles/views.py`, `config/urls.py`, `catalog/views.py`
- Modified: `templates/base.html`, `templates/catalog/browse.html`, `templates/catalog/song_detail.html`
- Updated: `README.md`, `DEVELOPMENT_PROGRESS.md`

Existing staged and untracked work was preserved. No commit was created and nothing was pushed. Playlist functionality was not started.

## Remaining note

The login template shows demo-account hints. Remove those hints before exposing the application publicly.
