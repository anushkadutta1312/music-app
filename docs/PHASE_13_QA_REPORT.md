# Phase 13 — Final UI Polish, Responsive QA and End-to-End Verification

**Date:** 2026-11-27  
**Result:** Complete with documented deployment and playback limitations.

## Scope and pages audited

The existing Django templates, URL routes, view/form behavior, styles, JavaScript player, prior phase reports, and the current automated suite were reviewed. Browser review covered the home page; registration and login; member and admin dashboards; profile and profile editing; catalogue search and artist/genre filtering; song detail; catalogue management; favourites; playlist list and populated playlist; empty dashboard, favourites and playlist states; and the shared player.

Playlist create/edit/delete, song addition/removal/reordering, ownership boundaries, CSRF, and unavailable-track handling were also checked against the relevant automated tests and Phase 10/12 browser evidence. No new catalogue or social features were added.

## Defects found and fixes

- **Public demo-password hint:** Removed the seeded account/password panel from `templates/accounts/login.html`. Synthetic predictable passwords remain only in the local `catalog/management/commands/seed_data.py` fixture and tests; they are not shown in the public-facing login page. Documentation now says not to seed or use these accounts in public deployments.
- **Logout mutation by GET:** `accounts/views.py` now requires POST for logout. Tests confirm GET returns 405 without ending the session and a POST without a valid CSRF token returns 403.
- **Native form validation disabled:** Removed `novalidate` from login, registration, profile-edit and playlist forms so the browser can provide required-field feedback. Server-side form validation remains in place.
- **Admin dashboard heading/badge collision:** `templates/accounts/admin_dashboard.html` and `static/css/style.css` now allow the heading and role badge to wrap without overlap at narrow widths.
- **Unavailable cover images in favourites:** `templates/profiles/favourites.html` now shows the same music placeholder used by catalogue cards when a remote image cannot load, instead of leaving a broken-image icon.
- **Stale home-page progress:** `templates/index.html` now describes Phases 1–12 as complete and Phase 13 as underway.
- Added visible keyboard-focus styling and responsive wrapping/stacking for navigation, dashboard columns and form grids in `static/css/style.css` and the related templates.

## Responsive browser results

The browser viewport override was available, so all requested sizes were tested as CSS viewport dimensions rather than estimated from a resized window:

| Viewport | Result |
| --- | --- |
| 360 × 800 | No horizontal overflow on audited pages; admin heading and badge do not overlap. |
| 390 × 844 | No horizontal overflow on audited pages; admin heading and badge do not overlap. |
| 768 × 1024 | No horizontal overflow on audited pages; admin heading and badge do not overlap. |
| 1366 × 768 | No horizontal overflow on audited pages; admin heading and badge do not overlap. |

The overflow check compared `document.documentElement.scrollWidth` with `window.innerWidth`. It covered home, member dashboard, profile, catalogue, song detail, favourites, playlist list and admin dashboard. The shared player remained present on each page; visible controls were checked on the catalogue and song detail pages. Catalogue cards stack on narrow viewports, navigation wraps, and the mobile capture remains readable when scrolled.

## Player checks

- No autoplay: newly loaded pages showed the idle “Ready — playback starts only when you choose a track” state.
- Play and pause: starting Showdown changed the player to Playing; pause changed the state to Paused.
- Seek: the seek control accepted a position change.
- Volume and mute: volume accepted 0.35; mute changed to Unmute and restored through the player control.
- Next and previous: after waiting for Showdown to load, Next changed the selected track to Bittersweet and Previous returned to Showdown.
- Missing audio feedback: catalogue entries without a sample display “Audio sample not available”. Playlist queue filtering and skipping unavailable tracks are covered in `playlists/tests_playback.py` and the Phase 12 evidence `screenshots/ui/phase12_04_playlist_skip_missing.jpg`.
- **Known limitation:** full-page navigation resets the current track. Playback persistence would require a broader client-side navigation change and was not attempted in this QA phase.

## Security and deployment review

- The complete automated suite covers role authorization, playlist/favourite ownership, CSRF-protected mutations, POST-only changes and form validation. The Phase 13 additions verify login-page credential hints are absent and logout rejects GET and CSRF-less POST.
- Production settings require `DJANGO_SECRET_KEY` and explicit `DJANGO_ALLOWED_HOSTS`, reject wildcard hosts, enable HTTPS redirects, and mark session/CSRF cookies secure. `DJANGO_DEBUG` defaults to development mode; production must set it to `False`.
- `python manage.py check --deploy` was run with production mode, a temporary generated key, explicit local test hosts, and one-year HSTS. Django reported two warnings: `SECURE_HSTS_INCLUDE_SUBDOMAINS` and `SECURE_HSTS_PRELOAD` are not enabled. These were left off because they should only be enabled after confirming every affected hostname is HTTPS-only. This is a deployment configuration decision, not a code defect.
- No real credential or secret value was added to source code or this report. The development secret is generated at runtime when unset; production refuses to start without an environment secret.

## Automated verification

| Check | Result |
| --- | --- |
| `python manage.py check` | Passed: no issues. |
| `python manage.py test --verbosity=2` | Passed: 125 tests in 367.591 seconds. |
| `python manage.py makemigrations --check --dry-run` | Passed: no changes detected. |
| `python manage.py check --deploy` | Completed with the two HSTS policy warnings described above. |

The automated suite used Django's in-memory test database. The populated project `db.sqlite3` was not reset, replaced, or seeded during this phase.

## Database integrity and baseline

Read-only SQLite checks returned `PRAGMA integrity_check = ok` and no rows from `PRAGMA foreign_key_check`. The current live counts are:

| Table data | Original requested baseline | Current count |
| --- | ---: | ---: |
| Users | 12 | 12 |
| Profiles | 12 | 12 |
| Songs | 55 | 60 |
| Artists | 20 | 21 |
| Genres | 10 | 11 |
| SongArtist rows | 59 | 64 |
| SongGenre rows | 94 | 99 |
| Favourites | 54 | 54 |
| Playlists | 15 | 15 |
| PlaylistSong rows | 70 | 70 |

The difference is the five playback samples and their one sample artist, one sample genre and five relationship rows in each junction table. All five sample audio paths recorded in the database resolve to existing MP3 files under `media/audio/samples/`. Checks found no duplicate artist names, genre names, song-artist links, song-genre links or playlist-song links.

## Screenshots

Genuine browser screenshots are stored under `screenshots/final/`:

- `phase13_01_home.jpg`
- `phase13_02_login.jpg`
- `phase13_03_registration.jpg`
- `phase13_04_member_dashboard.jpg`
- `phase13_05_profile.jpg`
- `phase13_06_profile_edit.jpg`
- `phase13_07_catalogue.jpg`
- `phase13_08_admin_dashboard.jpg`
- `phase13_09_catalogue_management.jpg`
- `phase13_10_song_detail_playing.jpg`
- `phase13_11_favourites.jpg`
- `phase13_12_playlists.jpg`
- `phase13_13_populated_playlist.jpg`
- `phase13_14_empty_member_dashboard.jpg`
- `phase13_15_empty_favourites.jpg`
- `phase13_16_empty_playlists.jpg`
- `phase13_17_mobile_catalogue.jpg` (full-page capture at 360 × 800)
- `phase13_18_desktop_catalogue.jpg`

## Files changed

Phase 13 changes cover `config/settings.py`, `.env.example`, `accounts/views.py`, `accounts/tests_auth.py`, `templates/accounts/`, `templates/catalog/`, `templates/profiles/favourites.html`, `templates/playlists/`, `templates/base.html`, `templates/index.html`, `static/css/style.css`, `README.md`, `DEVELOPMENT_PROGRESS.md`, `docs/AUTHENTICATION_AND_PERMISSIONS.md`, `docs/database/SAMPLE_DATA_REPORT.md`, and `screenshots/README.md`. New evidence is in `screenshots/final/`; this report is `docs/PHASE_13_QA_REPORT.md`.

No models, database schema, migrations or seed-command logic were changed for Phase 13. No Git commit or push was made; the existing staged and untracked project work remains in place.

## Remaining limitations

1. Player state resets on full-page navigation.
2. HSTS subdomain and preload settings require a deployment-specific HTTPS decision.
3. Predictable synthetic seed accounts remain for local academic evaluation and must not be used in public deployments.
4. Phase 14 final documentation/submission preparation remains to be completed.
