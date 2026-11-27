# Phase 12 — Music Playback Integration Report

**Status:** Implemented; automated suite and core browser behavior verified  
**Date:** 2026-11-27

## Delivered

- Added an optional `Song.audio_file` field using `catalog/migrations/0002_song_audio_file.py`. Existing songs remain valid with an empty audio field. The migration only adds this field; it does not change existing relationships or rows.
- Configured Django development media serving with `MEDIA_URL` and `MEDIA_ROOT`. `Song.audio_url` only exposes a file that exists in storage, so old catalogue songs and stale file references display as unavailable.
- Added the optional MP3 upload to the existing `SongForm` and bound file uploads in the existing create and edit views. The form posts as multipart and applies an MP3 extension validator.
- Added a reusable player to `templates/base.html` and `static/js/player.js`. It supports play/pause, previous/next, seeking, volume and mute. The selected page supplies its queue from playable controls; entries without audio are excluded.
- Added queue controls to catalogue browsing, song details, favourites and playlist details. Playlist ordering is preserved when building the playable queue.
- Added `python manage.py load_playback_samples`, an idempotent command that creates the credited sample artist, genre, songs and relationships. It reported five new songs on its first run and no new songs on its second run.

## Audio samples and licensing

Five MP3 files (26,521,937 bytes total) are stored under `media/audio/samples/`. Each is attributed to Kevin MacLeod and credited under CC BY 4.0. Track pages and the requested credit strings are recorded in [`media/audio/ATTRIBUTION.md`](../media/audio/ATTRIBUTION.md); the official [Incompetech licensing FAQ](https://incompetech.com/music/royalty-free/faq.html) and [Creative Commons BY 4.0 terms](https://creativecommons.org/licenses/by/4.0/) are linked there as well. The application links the attribution page from the player. No sample audio was edited.

The five included tracks are Carefree, Monkeys Spinning Monkeys, Sneaky Snitch, Bittersweet and Showdown. The original 55 catalogue songs remain in place; the five sample songs are additive. Existing commercially released catalogue entries are not given playable audio without a documented reusable source.

## Verification

### Automated

- `.\.venv\Scripts\python.exe manage.py check` — passed with no issues.
- `.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run` — passed; no model changes are missing from migrations.
- `.\.venv\Scripts\python.exe manage.py test --verbosity=2` — **122 tests passed**, 0 failures, using Django's in-memory test database (308.124 seconds).
- The playback-specific tests comprise 5 in `catalog/tests_playback.py`, 2 in `profiles/tests_playback.py` and 3 in `playlists/tests_playback.py`.

### Browser

Verified against the running local application using the member demo account:

- Catalogue sample began playing; the shared controls showed the active title, artist, duration and playing state.
- Pause and resume changed the player state. The seek control changed the playback position. Volume changed to 0.35 and the mute action changed the control to Unmute.
- Previous and next changed the active track in the catalogue queue.
- Playback began from a song detail page and from the favourites queue.
- Playlist Play All used the playlist order. The playlist had five tracks without audio between Showdown and Bittersweet; advancing from Showdown selected Bittersweet directly, confirming unavailable entries were skipped.
- Older catalogue and playlist songs displayed “Audio sample not available”. The media files loaded and played from local development media URLs.

Genuine browser captures are in `screenshots/ui/phase12_*.jpg`. The available in-app browser showed a narrow window layout, but did not expose device-size emulation; a dedicated mobile viewport check is not claimed and remains a Phase 13 QA item.

## Database preservation and integrity

The source database was not reset, reseeded, or used as the automated test database. The playback migration was applied to the existing populated `db.sqlite3`. Browser verification temporarily added one favourite and two playlist-song links for the demo member; those exact links were removed after verification. The final database counts are:

| Table | Rows |
|---|---:|
| `accounts_userprofile` | 12 |
| `catalog_genre` | 11 |
| `catalog_artist` | 21 |
| `catalog_song` | 60 |
| `catalog_songartist` | 64 |
| `catalog_songgenre` | 99 |
| `profiles_favourite` | 54 |
| `playlists_playlist` | 15 |
| `playlists_playlistsong` | 70 |

The original counts (10 genres, 20 artists, 55 songs, 59 song-artist links and 94 song-genre links) are retained with five additive sample tracks and their relationships. `PRAGMA integrity_check` returned `ok`; `PRAGMA foreign_key_check` returned no violations.

## Files created or changed

- **Created:** `catalog/migrations/0002_song_audio_file.py`, `catalog/management/commands/load_playback_samples.py`, `catalog/tests_playback.py`, `profiles/tests_playback.py`, `playlists/tests_playback.py`, `static/js/player.js`, `templates/catalog/_playback_track_control.html`, `docs/PHASE_12_PLAYBACK_REPORT.md`, `media/audio/ATTRIBUTION.md`, five files in `media/audio/samples/`, and five browser screenshots in `screenshots/ui/`.
- **Changed:** `.gitignore`, `DEVELOPMENT_PROGRESS.md`, `README.md`, `catalog/models.py`, `catalog/forms.py`, `catalog/views.py`, `config/settings.py`, `config/urls.py`, `playlists/views.py`, `screenshots/README.md`, `static/css/style.css`, `templates/base.html`, `templates/catalog/browse.html`, `templates/catalog/song_detail.html`, `templates/catalog/song_form.html`, `templates/playlists/detail.html`, and `templates/profiles/favourites.html`.
- A temporary screenshot receiver used during browser capture was removed after the screenshots were saved.

## Known limits and follow-up

- The HTML5 player and queue are shared across pages, but a full page navigation reloads the JavaScript player and resets its current track and queue. Playback does not continue uninterrupted between navigations.
- The included media route is enabled in Django `DEBUG` mode for local development. Production static/media hosting has not been configured.
- The file validator checks the `.mp3` extension; it does not inspect file contents. Uploads are available only through the existing ADMIN-protected catalogue forms.
- Device-emulated mobile verification remains pending. No new catalogue features or Phase 13 work was started.

## Git status

No commit was created, no Git identity was configured, and nothing was pushed. Existing staged changes were left staged as found; Phase 12 work remains unstaged/untracked for review.
