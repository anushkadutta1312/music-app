# Academic Screenshots & Verification Evidence

This directory stores visual verification artifacts required for academic documentation and project evaluation of the **Music App**.

---

## Screenshot Categories

### 1. Database Inspection (`screenshots/dbms/`)
- `database_structure.jpg` shows the existing project database open in DB Browser, including the app tables and Django support tables.
- Schema details, constraints, and live row counts are documented in `database/ACTUAL_SCHEMA_AUDIT.md`.

### 2. SQL Practical Execution (`screenshots/dbms/`)
- `09_dml_rollback.jpg` shows successful INSERT/UPDATE/DELETE practical execution and a zero-row result after deletion.
- The nine scripts and all 15 query results are documented in `docs/DBMS_SQL_PRACTICAL.md` and independently verified by `database/run_sql_practical.py`.

### 3. Application User Interface (`screenshots/ui/`)
- Responsive modern music dashboard.
- Song and artist browsing, detail pages, and genre filters.
- User registration and login forms with validation errors.
- Playlist management interface (CRUD operations).
- AJAX/Fetch API dynamic search interaction in action.
- Working audio player widget embedded and active.

### Phase 12 Playback Evidence
- `phase12_01_catalogue_playing.jpg`: active sample playback in the catalogue, including an unavailable catalogue track.
- `phase12_02_favourites_playing.jpg`: active playback from the member's favourites page.
- `phase12_03_playlist_queue.jpg`: playlist Play All state.
- `phase12_04_playlist_skip_missing.jpg`: playlist playback after advancing past five songs without audio to the next playable sample.
- `phase12_05_narrow_view.jpg`: playback page captured in the available narrow in-app browser window. This is visual evidence only; device-emulated mobile testing was unavailable.

The sample audio is credited in `media/audio/ATTRIBUTION.md` and linked from the shared player.

### Phase 13 Final UI Evidence

The Phase 13 browser captures are stored in `screenshots/final/`. They include the home, login, registration, member and admin dashboards, profile, catalogue, catalogue management, song detail with playback, favourites, playlist list/detail, empty states, and a full-page catalogue capture at the 360 px mobile viewport. The 360, 390, 768 and 1366 px viewport checks are recorded in `docs/PHASE_13_QA_REPORT.md`. The login capture reflects removal of the in-page demo-password hint. Older Phase 7 screenshots under `screenshots/ui/` are historical and may show that earlier interface.

Final capture filenames use the `phase13_` prefix in `screenshots/final/`; numbered captures are genuine screenshots saved from the local browser session. The mobile catalogue image is a full-page capture at 360 × 800 CSS pixels.

The Phase 11 DBMS screenshot set contains representative UI evidence for the live schema and the safely rolled-back DML run; it does not contain a separate image for every SELECT demonstration.
