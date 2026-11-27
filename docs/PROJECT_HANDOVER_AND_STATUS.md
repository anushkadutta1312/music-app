# Music App — Project Handover and Status

**Audit date:** 27 November 2026  
**Scope:** Repository, code, SQLite database and available evidence inspection. No application code, migrations, or database records were changed during this audit.

## 1. Project objective

Music App is a college project combining DBMS concepts with a Django full stack application. Its intended product is a manageable music discovery and personal playlist application, with separate ADMIN and MEMBER roles. It is not a social network.

The local repository does not contain an identifiable assignment brief (`.doc`, `.docx` or `.pdf`) in the project files inspected. The academic scope recorded here therefore comes from the supplied handover text. Treat the college's original brief as authoritative if it becomes available.

## 2. Academic requirements and intended scope

The requested full stack areas are HTML5, CSS3, vanilla JavaScript, Python/Django, Django views/templates/models/ModelForms/ORM, SQLite, CRUD, registration/login/logout, role authorization, Fetch/AJAX, responsive UI, validation, CSRF, Git/GitHub, and setup documentation.

The requested DBMS areas are at least six meaningful application tables, PK/FK and one-to-many/many-to-many relations, constraints, ER diagram, relational schema, data dictionary, normalization examples, and at least 12 meaningful SQL demonstrations covering the operations named in the handover. The SQL exercises must run in DB Browser for SQLite against this project's Django `db.sqlite3`.

Intended app features are authentication and profiles; catalogue browsing, search and filtering; personal favourites and playlists; ADMIN catalogue management; and a provider integration only after access, embedding, cost, licensing and identifier details are verified. Chat, social graph/feed and AI recommendations are expressly out of scope. Playback is not part of Phase 8.

## 3. Required technology

The repository uses Python, Django, SQLite, Django ORM, HTML templates, CSS and vanilla JavaScript. The project must remain on this stack; DB Browser for SQLite and Git/GitHub are part of the academic workflow.

## 4. Current architecture

- Django project/configuration: `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py`, and `manage.py`.
- Installed project apps: `accounts`, `catalog`, `playlists`, and `profiles`; Django admin, auth, contenttypes, sessions, messages and staticfiles are also installed.
- App code includes models, views, forms, URL routes, admin registration and migrations. Templates are in the top-level `templates/`; styling is in `static/css/style.css`.
- Sample data command: `catalog/management/commands/seed_data.py` (`seed_data`).
- Tests are in `accounts/`, `catalog/`, `profiles/`, and `playlists/` test modules. Additional support scripts are under `database/`.
- Documentation includes database design, schema, constraints, dictionary, normalization, ER diagram/source, sample-data report, authentication notes, roadmap, progress, README and checklist.
- Screenshots and saved HTML captures exist under `screenshots/ui/`. They show the home/authentication/profile/dashboard and catalogue-management/access-denied areas.
- The local SQLite file is `db.sqlite3`; Django settings point to it directly.

## 5. Existing database schema and verification

The nine application tables are present:

| Table | Current rows | Purpose |
|---|---:|---|
| `accounts_userprofile` | 12 | One profile and role per Django user |
| `catalog_genre` | 10 | Genre catalogue |
| `catalog_artist` | 20 | Artist catalogue |
| `catalog_song` | 55 | Song metadata |
| `catalog_songartist` | 59 | Song/artist many-to-many association |
| `catalog_songgenre` | 94 | Song/genre many-to-many association |
| `profiles_favourite` | 54 | User/song favourites |
| `playlists_playlist` | 15 | User-owned playlists |
| `playlists_playlistsong` | 70 | Ordered playlist/song association |

The database also contains Django auth, admin, content type, migration and session tables. Counts above were read directly from `db.sqlite3` in SQLite read-only mode and match the handover's reported sample counts. `PRAGMA integrity_check` returned `ok`; `PRAGMA foreign_key_check` returned no rows. This establishes present file integrity and referential integrity, but a previous-state backup or baseline was not available, so historic inserts/updates/deletes cannot be independently ruled out.

The models and initial migrations define the expected application entities, unique fields/relations and song duration check. Full constraint-by-constraint live inspection through DB Browser was not performed; the model/migration definitions and SQLite integrity checks were inspected. No reset, reseed, migration, or destructive SQL was run.

## 6. Phase 8 interruption analysis

Phase 8 is substantially present in source, despite the earlier agent's incomplete progress report:

- ADMIN-protected song, artist and genre create/edit/delete views and management list routes exist.
- Deletion views display a confirmation page on GET and perform deletion on POST. Song deletion explains that association rows, playlist entries and favourites cascade, while artists/genres remain.
- `SongForm` validates selected artists and genres and synchronizes the explicit junction records inside a database transaction. Artist and genre ModelForms are present.
- Member catalogue browsing searches title, album and artist; filters by genre and artist; paginates at 12 per page; and retains query parameters. Management song and artist lists also paginate.
- Catalogue/detail views use `prefetch_related`/`select_related` in several paths to reduce N+1 queries.
- Django routes and templates exist for the CRUD and browse flows.

Phase 8 is **not verified complete**. Existing tests cover catalogue model constraints/associations and authentication/permissions; no dedicated view/form integration tests for all CRUD paths, search/filter combinations, pagination, delete impact, relationship reconciliation, or invalid form submissions were confirmed. No live browser run of Phase 8 was performed during this audit. Screenshots include a catalogue management page, but do not demonstrate the complete CRUD/browse workflow. There is also some duplicated search/pagination logic between the public catalogue and admin song list, which is maintainability debt rather than proof of a functional defect.

The source includes explicit external provider fields/IDs in catalogue models/data, but no verified playback integration should be claimed. Playback is correctly outside Phase 8 and remains pending provider/licensing review.

## 7. Feature status

Statuses indicate evidence found in this audit, not earlier progress claims.

| Area | Status | Evidence / missing work |
|---|---|---|
| Repository and environment setup | PARTIALLY COMPLETE | Django project, `.venv`, requirements, config and `.env.example` exist. Git has no commits; repository files are untracked. Setup should be followed from a clean environment before calling it reproducible. |
| Database architecture | COMPLETE | Nine application tables, migrations, model relationships and constraints are defined; live row counts and SQLite integrity checks pass. |
| ER diagram and relational schema | COMPLETE | ER source/PNG and relational schema documentation exist. Validate diagram against any later model changes before submission. |
| Normalization documentation | COMPLETE | `docs/database/normalization.md` exists and describes 1NF–3NF. Confirm the examples match final schema during submission review. |
| Sample data | COMPLETE | `seed_data` command exists; live counts match all ten reported entity counts. The automated idempotence test passed: the second command run created zero new rows in each entity. |
| SQL practical demonstrations | NOT STARTED | `sql/` contains a README, but no SQL demonstration script/evidence set was found. Need at least 12 executed queries in DB Browser against this same DB. |
| Authentication | COMPLETE | Registration, login, POST logout, profile and dashboard routes/templates exist; tests cover core flows. |
| Role-based authorization | COMPLETE | ADMIN/MEMBER role and server-side checks exist; tests exercise member denial and role escalation prevention. Recheck each new CRUD endpoint in integration tests. |
| Browser verification | PARTIALLY COMPLETE | Saved screenshots/HTML cover auth/dashboard/profile and catalogue-management/access-denied pages. Current browser verification and full Phase 8 interaction were not re-established. |
| Catalogue CRUD (Phase 8) | PARTIALLY COMPLETE | Admin forms, routes, views, templates and POST deletion confirmations exist. Dedicated CRUD and relationship tests plus browser verification remain. |
| Catalogue browsing | PARTIALLY COMPLETE | Browse/search/filter/detail routes and templates exist; test complete member-facing flow and catalogue empty/error cases. |
| Search and filtering | PARTIALLY COMPLETE | ORM filters cover title/artist/album plus genre/artist; combined behavior and invalid filter input need automated verification. |
| Pagination | PARTIALLY COMPLETE | `Paginator` is used in member browse and some admin lists. Genre management does not paginate; verify expected behavior and querystring preservation. |
| Favourites | PARTIALLY COMPLETE | Favourites model/table and sample rows exist. User-facing add/remove/list flows and ownership authorization were not found/verified. |
| Playlist management | PARTIALLY COMPLETE | Playlist and ordered playlist-song models/table and sample rows exist. User-facing CRUD/song-management views and ownership authorization were not found/verified. |
| Fetch/AJAX functionality | NOT STARTED | No meaningful Fetch/XHR interaction was found in project static/templates/views. Implement one required interaction and test CSRF handling. |
| Music playback | NOT STARTED | Provider fields/IDs exist, but no verified playback. Research provider access, embedding, licensing and costs before choosing integration. |
| Responsive UI | PARTIALLY COMPLETE | CSS and screenshot artifacts exist; responsive breakpoints and current behavior across viewport sizes were not independently verified. |
| GitHub documentation | PARTIALLY COMPLETE | README and setup/project notes exist. There are no commits and no remote/repository URL was verified; GitHub publication information is pending. |
| Final academic submission evidence | PARTIALLY COMPLETE | ER/schema/normalization docs and UI captures exist. SQL DB Browser evidence, final screenshots, repository information and a checked submission package remain. |

## 8. Git status

At audit time, `git status --short --branch` reported `## No commits yet on main`, followed by untracked project files/directories (including source, docs, screenshots, SQL, config and requirements). `git log` reports that `main` has no commits. Thus there is no committed baseline against which to identify prior Phase 8 changes or distinguish them from all other in-progress files. `.venv` and `db.sqlite3` do not appear in the untracked status output (ignored by Git rules). No changes were discarded, staged or committed.

## 9. Django check and test results

- `python manage.py check` using `.venv` completed successfully: **System check identified no issues (0 silenced).**
- `python manage.py test --verbosity=2` completed using the project `.venv`: **Ran 39 tests in 326.673 seconds — OK** (exit code 0).
- The passing tests include authentication/authorization, catalogue model constraints and relations, seed-data population/idempotence, playlist/favourite model behavior and cascade checks. They do not provide full Phase 8 view/form integration coverage.
- Test startup applied migrations to Django's in-memory test database only; project migrations were not run against the working database by the audit.

## 10. Database integrity findings

All expected application tables and counts are present. SQLite reports `integrity_check = ok` and no foreign-key violations. These are read-only checks. There is no known clean backup/baseline for comparison, so the audit cannot certify whether records were changed historically. The browser tool DB Browser evidence requirement remains open; raw SQLite inspection is not a substitute for screenshots from DB Browser.

## 11. Known technical problems and limitations

1. No commit history exists, so the “18 changed files” Phase 8 report cannot be verified against a previous revision; all working project files are untracked.
2. The complete Django test suite passes but takes about 5.5 minutes in this environment, which makes frequent full-suite iterations slow.
3. Catalogue CRUD and discovery have implementation but need focused integration tests and live browser verification.
4. Favourites and playlist tables/models are populated, but application workflows were not found/verified.
5. No required Fetch/AJAX feature or SQL practical scripts/evidence were found.
6. Browser screenshots and DB Browser SQL evidence are incomplete for final academic proof.
7. The project-local authoritative assignment document was not found.
8. Production settings currently default to `DEBUG=True` and an insecure fallback secret; review deployment settings before any public deployment. Do not use demo account credentials publicly.

## 12. Recommended development sequence

1. Add Phase 8 integration tests for admin CRUD/permissions, member browse, filters, pagination, form validation, relationship updates and safe deletion; then verify those flows in a browser.
2. Keep the full test suite green while implementing, and use focused test classes during iteration because the full run takes about 5.5 minutes.
3. Implement member favourites and playlist workflows with per-user server-side ownership checks and tests.
4. Add one useful Fetch API interaction with CSRF protection, and verify responsive layouts at representative screen widths.
5. Create and execute at least 12 SQL demonstrations in DB Browser against this `db.sqlite3`; capture evidence and complete GitHub/setup/submission documentation.

Music playback research and implementation should follow only if the course requires it and a provider's access, embedding, cost and licensing terms are established. It is not part of Phase 8.

## 13. Final submission checklist

- [ ] Confirm the original assignment brief and reconcile this scope with it.
- [ ] Complete and record Django check and test results.
- [ ] Verify catalogue CRUD, discovery, permissions and responsive behavior in a browser.
- [ ] Implement/test user-owned favourites and playlist workflows.
- [ ] Demonstrate a working Fetch interaction with CSRF.
- [ ] Confirm ER diagram, relational schema, data dictionary, constraints and normalization examples match the final models.
- [ ] Prepare at least 12 SQL examples and run them using DB Browser for SQLite against the same `db.sqlite3`.
- [ ] Capture application and DB Browser evidence.
- [ ] Verify setup from README, commit/publish the project as required, and record the repository URL.
- [ ] Package source, database documentation, evidence and setup instructions; exclude secrets and avoid exposing demo credentials publicly.
