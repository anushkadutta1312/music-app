# Phase 8 — Step 1: Catalogue Admin Permission Testing

**Date:** 27 November 2026  
**Scope:** Verify authorization for all catalogue-management routes and safe handling of catalogue deletion requests. No application views, models, forms, seed data, migrations, or database records were changed.

## Endpoints tested

The routes are declared in `catalog/urls.py` and are mounted under `/catalog/` by the project URL configuration.

| URL name | Route | Operation |
|---|---|---|
| `catalogue_manage` | `/catalog/manage/` | Management dashboard |
| `song_manage_list` | `/catalog/manage/songs/` | Song listing |
| `song_create` | `/catalog/manage/songs/create/` | Song creation |
| `song_update` | `/catalog/manage/songs/<int:pk>/edit/` | Song editing |
| `song_delete` | `/catalog/manage/songs/<int:pk>/delete/` | Song deletion |
| `artist_manage_list` | `/catalog/manage/artists/` | Artist listing |
| `artist_create` | `/catalog/manage/artists/create/` | Artist creation |
| `artist_update` | `/catalog/manage/artists/<int:pk>/edit/` | Artist editing |
| `artist_delete` | `/catalog/manage/artists/<int:pk>/delete/` | Artist deletion |
| `genre_manage_list` | `/catalog/manage/genres/` | Genre listing |
| `genre_create` | `/catalog/manage/genres/create/` | Genre creation |
| `genre_update` | `/catalog/manage/genres/<int:pk>/edit/` | Genre editing |
| `genre_delete` | `/catalog/manage/genres/<int:pk>/delete/` | Genre deletion |

## Permission test results

All 13 management URLs were exercised using Django's test client:

- **Anonymous visitor:** GET requests redirected to the login page. POST requests to every create, edit, and delete endpoint also redirected to login.
- **Authenticated MEMBER:** GET requests to every management URL returned HTTP 403. POST requests to every create, edit, and delete endpoint returned HTTP 403. Tests confirmed the sample song, artist and genre were unchanged.
- **Authenticated ADMIN:** GET requests to all 13 management pages returned HTTP 200. The fixture has the `ADMIN` profile role and is not staff, confirming application role authorization is sufficient.

## Destructive action and CSRF results

- GET requests to song, artist and genre delete endpoints returned confirmation pages and did not delete records.
- PUT requests did not delete records.
- With `Client(enforce_csrf_checks=True)`, missing/invalid CSRF tokens on delete POSTs returned HTTP 403 and preserved the records.
- Valid token-bearing POST requests deleted each target record. Deleting an artist or genre removed its junction row while preserving the song. Deleting the song removed its remaining junction rows.

`CsrfViewMiddleware` is enabled in Django middleware, and the delete confirmation template includes a CSRF token in its POST form. No catalogue authorization or CSRF security defect was found. Unexpected methods such as PUT currently render the confirmation page with HTTP 200 rather than returning 405; they do not mutate data, so this is a method-response consistency issue rather than an authorization bypass.

## Files modified

- Added `catalog/tests_views.py` with seven focused integration tests covering role access, unauthorized mutations, deletion methods, CSRF enforcement and related-row behavior.
- Added this report at `docs/PHASE_8_STEP_1_REPORT.md`.
- No existing staged changes were unstaged or discarded. The two new files are separate working-tree additions; no commit or push was created.

## Verification

Commands were run with the project's `.venv` Python interpreter:

| Command | Result |
|---|---|
| `python manage.py check` | **Passed:** System check identified no issues (0 silenced). |
| `python manage.py test catalog.tests_views --verbosity=2` | **Passed:** Ran 7 tests in 1.975 seconds; OK. |
| `python manage.py test --verbosity=2` | **Passed:** Ran 46 tests in 336.291 seconds; OK. |

The test runner used Django's in-memory test database. The project's populated `db.sqlite3` was not modified. No migrations were created or applied to the project database.

## Step 1 outcome

Catalogue management authorization, delete method handling and CSRF behavior passed the focused tests. No application code change was required. Stop here; do not proceed to Phase 8 Step 2 without approval.
