# Master Development Roadmap

This document defines the 14 sequential implementation phases for the **Music App** project.

---

## Phase Schedule & Status

### Phase 1: Repository Initialization
- **Status**: **COMPLETE AND VERIFIED**
- Setup Git version control, core directory hierarchy (`docs/`, `database/`, `sql/`, `screenshots/`), and baseline configuration.

### Phase 2: Python and Django Environment Setup
- **Status**: **COMPLETE AND VERIFIED**
- Created `.venv/`, installed Django 6.1.3, pinned dependencies in `requirements.txt`, initialized Django project `config/`, created applications (`accounts`, `catalog`, `playlists`, `profiles`), configured SQLite, applied initial system migrations, and verified HTTP 200 server response.

### Phase 3: Project Scope Finalization & Identity Correction
- **Status**: **COMPLETE AND VERIFIED** *(Current Phase)*
- Clarified and finalized project scope as a **Simple Full Stack Music Application** (music discovery and playlist management).
- Removed all social networking, messaging, chat, and AI recommendation references across all project documentation.

---

### Phase 4: Database Architecture & ER Design *(Next Phase)*
- **Status**: **PENDING**
- Finalize formal entity-relationship (ER) specifications for the 10 proposed music app tables.
- Verify normalization (1NF, 2NF, 3NF).
- Document column specifications, data types, and constraints (PK, FK, UNIQUE, NOT NULL, DEFAULT, CHECK).
- Create conceptual/logical ER diagrams.

### Phase 5: Django Database Implementation & Migrations
- **Status**: **PENDING**
- Implement Django models across `accounts`, `catalog`, `playlists`, and `profiles`.
- Define model-level constraints and Meta configurations (`UniqueConstraint`, `CheckConstraint`).
- Generate and execute migrations (`makemigrations`, `migrate`).
- Inspect created schema in DB Browser for SQLite.

### Phase 6: Reproducible Sample Seed Data
- **Status**: **PENDING**
- Create reproducible seed data script (genres, artists, songs with metadata, external playback links).
- Verify population in SQLite and DB Browser.

### Phase 7: Authentication, User Roles & Permissions
- **Status**: **PENDING**
- Implement registration, login, logout, and profile management using Django authentication.
- Configure `ADMIN` and `MEMBER` roles with server-side access control decorators (`@login_required`).

### Phase 8: Music Catalogue Backend & CRUD Logic
- **Status**: **PENDING**
- Implement song browsing, song detail views, artist browsing, and genre filtering.
- Implement catalogue management views restricted to `ADMIN`.
- Implement catalogue search views.

### Phase 9: Music Application Frontend & Fetch API Search
- **Status**: **PENDING**
- Design modern, dark-themed responsive music interface (HTML5, CSS3, optional Bootstrap).
- Implement dashboard (recent songs, popular tracks, genres, user playlists).
- Implement dynamic, asynchronous search using JavaScript Fetch API without page reload.

### Phase 10: Favourites and Playlists (Full CRUD)
- **Status**: **PENDING**
- Implement user favourites (add, list, remove, duplicate prevention).
- Implement playlist full CRUD (create, view, rename, edit description, add/remove songs, track ordering, delete).
- Enforce strict server-side ownership authorization.

### Phase 11: Music Playback Integration
- **Status**: **PENDING**
- Integrate chosen external playback provider (e.g. YouTube official embed player or Jamendo API).
- Connect playback trigger from song lists and playlist views.
- Test preview playback across devices.

### Phase 12: Database & SQL Practical Demonstrations
- **Status**: **PENDING**
- Author and verify minimum 12 academic SQL scripts in `sql/` (INSERT, UPDATE, DELETE, and SELECT with JOINs, GROUP BY, aggregations, and subqueries).
- Execute queries directly against `db.sqlite3` in DB Browser for SQLite.

### Phase 13: Testing, Quality Assurance & Security Review
- **Status**: **PENDING**
- Verify CSRF protection, input validation, and role authorization.
- Test responsive layout across mobile and desktop.
- Verify no out-of-scope features exist.

### Phase 14: Final Documentation, Evidence & Submission
- **Status**: **PENDING**
- Collect DB Browser and UI verification screenshots in `screenshots/`.
- Finalize `DEVELOPMENT_PROGRESS.md` and `REQUIREMENTS_CHECKLIST.md`.
- Prepare final Git commit and GitHub submission package.
