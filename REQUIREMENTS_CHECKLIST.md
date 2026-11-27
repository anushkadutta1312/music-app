# Academic Requirements & Compliance Checklist

This document tracks all formal academic requirements for the **Music App** (Full Stack + DBMS project).

### Status Classification:
- **Pending**: Requirement identified and planned, but implementation not yet started.
- **Implemented**: Requirement coded in application or schema.
- **Tested**: Requirement verified locally via manual/automated tests or query execution.
- **Verified**: Fully documented with screenshots/demonstrations and ready for academic submission.

---

## 1. Database Management System (DBMS) Requirements

| ID | Requirement Description | Target Specification | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **DB-01** | Minimum 6 Application Tables | At least 6 meaningful tables (9 implemented: UserProfile, Artist, Genre, Song, SongArtist, SongGenre, Favourite, Playlist, PlaylistSong) | **Verified** | 9 application tables populated with realistic sample data |
| **DB-02** | Primary Keys | Defined surrogate PK (`id`) for every application table | **Verified** | Clustered integer PKs populated across 10 tables |
| **DB-03** | Foreign Keys | Appropriate foreign keys enforcing referential integrity | **Verified** | `PRAGMA foreign_key_check` confirmed 0 violations |
| **DB-04** | UNIQUE Constraints | Prevent duplicate entries (genre names, artist names, unique favourites, unique playlist songs) | **Verified** | Tested via unit tests and idempotent seed command |
| **DB-05** | NOT NULL Constraints | Enforced non-nullable fields on critical metadata columns | **Verified** | Enforced across all required fields |
| **DB-06** | DEFAULT Values | Reasonable defaults for timestamps, ordering, boolean flags | **Verified** | Populated defaults: role, privacy, positions, timestamps |
| **DB-07** | CHECK Constraints | At least one check constraint (implemented: `duration_seconds > 0`, `position >= 1`, `release_year >= 1900`) | **Verified** | Confirmed on all 55 songs and 70 playlist tracks |
| **DB-08** | One-to-Many (1:M) Relationships | Meaningful 1:M relationships (e.g., User -> Playlist, Artist -> SongArtist) | **Verified** | Populated and verified across models |
| **DB-09** | Many-to-Many (M:N) Relationship | Explicit junction tables for M:N relationships (SongArtist, SongGenre, Favourite, PlaylistSong) | **Verified** | 59 SongArtist, 94 SongGenre, 54 Favourite, 70 PlaylistSong |
| **DB-10** | Database Normalization (1NF) | Elimination of repeating groups; atomic attribute values | **Verified** | Documented in `docs/database/normalization.md` |
| **DB-11** | Database Normalization (2NF) | Elimination of partial functional dependencies on composite keys | **Verified** | Documented in `docs/database/normalization.md` |
| **DB-12** | Database Normalization (3NF) | Elimination of transitive functional dependencies | **Verified** | Documented in `docs/database/normalization.md` |
| **DB-13** | Unified Database Usage | Same Django-managed SQLite database (`db.sqlite3`) used for both app runtime & SQL practicals | **Verified** | Populated `db.sqlite3` active at project root |

---

## 2. SQL Practical Demonstrations (Minimum 12 Queries)

| ID | Query Category | Specific Description | Status | Evidence File |
| :--- | :--- | :--- | :--- | :--- |
| **SQL-01** | INSERT | Insert a new artist record | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-02** | INSERT | Insert a new song with metadata | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-03** | INSERT | Add a song to a playlist (junction table insertion) | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-04** | UPDATE | Update song metadata (e.g. duration, title) | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-05** | UPDATE | Rename playlist and edit description | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-06** | DELETE | Remove a song from a playlist | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-07** | DELETE | Delete an entire playlist with cascading items | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-08** | SELECT (Simple & Filter) | Retrieve all songs belonging to a selected genre | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-09** | SELECT (INNER JOIN) | Fetch songs joined with their artists and genres | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-10** | SELECT (M:N JOIN) | Retrieve all songs in a specific playlist ordered by track order | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-11** | SELECT (Aggregate & GROUP BY) | Count total songs per genre or songs per artist | `Pending` | `sql/queries.sql` (Phase 12) |
| **SQL-12** | SELECT (HAVING / Subquery) | Find playlists containing more than N songs or artists with above-average track counts | `Pending` | `sql/queries.sql` (Phase 12) |

---

## 3. Full Stack Application & Backend Requirements

| ID | Requirement Description | Target Specification | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **FS-01** | Complete CRUD Functionality | Full Create, Read, Update, Delete on Playlists and Favourites | `Pending` | Django views & templates (Phase 10) |
| **FS-02** | User Registration | Public registration form with server-side validation | **Verified** | `accounts/views.py` `register_view` |
| **FS-03** | User Login & Logout | Secure session-based authentication | **Verified** | `accounts/views.py` `login_view`, `logout_view` |
| **FS-04** | Role-Based Access Control | At least 2 roles: `ADMIN` (catalogue management) and `MEMBER` (playlists/favourites) | **Verified** | Enforced via `@admin_required` & `UserProfile.role` |
| **FS-05** | Server-Side Access Restrictions | Unauthorized users cannot edit or delete another user's playlists or access admin dashboard | **Verified** | Server returns HTTP 403 for unauthorized access |
| **FS-06** | CSRF Protection | Enabled on all state-mutating forms | **Verified** | Enforced on register, login, profile edit, logout |
| **FS-07** | Input Validation | Form-level & model-level validation on all inputs | **Verified** | Validation on username, email, passwords, profile fields |
| **FS-08** | Dynamic AJAX / Fetch API | Asynchronous search or favourite toggle without page reload | `Pending` | Vanilla JS + Fetch API (Phase 9) |

---

## 4. Frontend & User Interface Requirements

| ID | Requirement Description | Target Specification | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **UI-01** | HTML5 Semantic Structure | Proper header, nav, main, section, footer tags | **Verified** | Clean semantic master layout in `base.html` |
| **UI-02** | Responsive Styling | Mobile-friendly and desktop layout using modern CSS3 | **Verified** | Responsive dark theme in `static/css/style.css` |
| **UI-03** | Music Search & Discovery | Search songs, artists, and genres by query string | `Pending` | Search views and templates (Phase 9) |
| **UI-04** | External Audio Playback | Working audio player preview via external provider | `Pending` | YouTube / Jamendo integration (Phase 11) |
| **UI-05** | Modern Music Dashboard | Displays recent songs, popular tracks, genres, and user playlists | **Verified** | Member & Admin dashboards implemented |

---

## 5. Version Control & Documentation

| ID | Requirement Description | Target Specification | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **DOC-01** | Git Version Control | Clean commit history reflecting step-by-step progress | **Implemented** | Git repository initialized; code clean |
| **DOC-02** | Comprehensive README | Complete setup, architecture, and feature overview | **Verified** | Updated in `README.md` |
| **DOC-03** | Database Inspection Evidence | Screenshots showing tables and query results in DB Browser | `Pending` | `screenshots/` directory (Phase 12) |
| **DOC-04** | Progress & Checklist Tracking | Live tracking of all academic deliverables | **Verified** | Maintained in this file |
