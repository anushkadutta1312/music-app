# Music App

A database-driven Full Stack Music Discovery and Playlist Management Application.

---

## 1. Project Overview

**Music App** is a responsive, database-driven web application built for music enthusiasts to discover music, explore artists and genres, search for tracks, maintain a collection of favourite songs, and curate personal playlists.

Playback uses the native HTML5 audio element with five locally served, attribution-required sample tracks. Existing catalogue songs remain intact; songs without a documented reusable audio file are clearly marked unavailable.

This project is developed to fulfill the academic requirements for **Full Stack Web Development** and **Database Management Systems (DBMS)**. It emphasizes clean software architecture, relational database normalization (1NF, 2NF, 3NF), relational integrity constraints, server-side role-based access control (`ADMIN` vs. `MEMBER`), reproducible synthetic sample data, and practical SQL query demonstrations.

---

## 2. Project Identity & Objectives

- **Project Name**: Music App
- **Project Category**: Full Stack Music Discovery & Playlist Management Application
- **Core Objectives**:
  - Provide a clean, modern music discovery experience.
  - Deliver full CRUD functionality for user playlists and favourite songs.
  - Implement a normalized relational database schema (9 application tables) enforcing PK, FK, UNIQUE, NOT NULL, and CHECK constraints; model defaults are applied by Django.
  - Implement two distinct user roles: `ADMIN` (catalogue management) and `MEMBER` (favorites, playlists, profile) enforced on the server side.
  - Enable direct SQL practical demonstrations (minimum 12 queries: INSERT, UPDATE, DELETE, and SELECT with JOINs, aggregations, and subqueries) executed against the unified SQLite database.
  - Implement asynchronous search using JavaScript Fetch API without full page reload.

---

## 3. Technology Stack

### Frontend
- **HTML5**: Semantic markup for accessible, structured page layouts.
- **CSS3**: Custom responsive styling (modern dark-themed interface).
- **Vanilla JavaScript**: Client-side logic and DOM interactions.
- **Fetch API**: Asynchronous search and dynamic catalogue interactions without page reloads.

### Backend
- **Python (3.14.7)**: Core programming language.
- **Django (6.1.3)**: Web framework supplying MVT architecture, routing, views, templates, CSRF security, session management, and PBKDF2 password hashing.
- **Django Templates**: Server-side HTML rendering with dynamic navigation.
- **Django Forms / ModelForms**: Server-side data validation and sanitization.

### Database & ORM
- **SQLite 3 (`db.sqlite3`)**: File-based relational database.
- **Django Models / ORM**: Object-relational mapping bridging Python objects and SQL tables.
- **DB Browser for SQLite**: Visual tool for inspecting database schema, tables, and executing SQL demonstration queries.

### Version Control
- **Git**: Local distributed version control. A remote repository is not required for the current development phase.

---

## 4. Finalized Project Scope

### Approved In-Scope Features
1. **User Authentication & Profiles**: Registration, login, logout, password hashing, and role permissions (`ADMIN` and `MEMBER`).
2. **Music Dashboard**: Displaying recently added songs, popular tracks from real DB data, genres, featured artists, and personal playlists/favourites.
3. **Music Catalogue**: Browse songs with metadata, browse artists with track listings, browse genres, filter songs by genre, sorting, and pagination.
4. **Music Playback**: Native HTML5 playback for a small set of locally stored, CC BY 4.0 sample tracks. Commercial catalogue recordings are not included as audio.
5. **Favourite Songs**: Add/remove favourite songs, view personal favourites list, prevent duplicate entries, and strict user ownership.
6. **Playlist Management (Full CRUD)**: Create, view, rename, edit description, add/remove songs with `track_order`, delete playlists, and server-side authorization.
7. **Search & Fetch API**: Asynchronous search across songs, artists, and genres without full page reload.

### Strictly Out-of-Scope Features (Must NOT Exist)
- ❌ **No Social Networking**: No social feeds, timelines, or posts.
- ❌ **No Chat or Direct Messaging**: No user-to-user messaging, chatrooms, or conversation threads.
- ❌ **No Social Connections**: No friend requests, followers, following, or user matching.
- ❌ **No AI / Algorithmic Recommendations**: No machine learning or similarity recommendation engines.
- ❌ **No Messaging Notifications**: No notification tickers or message alert systems.

---

## 5. Repository Structure

```
music-social-network/              # Repository Root
│
├── manage.py                      # Django command-line execution utility
├── requirements.txt               # Pinned project dependencies
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git exclusion rules
├── README.md                      # Primary project overview and setup guide
├── DEVELOPMENT_PROGRESS.md        # Real-time tracking across 14 development phases
├── REQUIREMENTS_CHECKLIST.md      # Academic requirements compliance checklist
│
├── config/                        # Core project settings and URL configuration
│   ├── settings.py                # Django settings (apps, DB, static, templates)
│   └── urls.py                    # Master URL routing table
│
├── accounts/                      # App: UserProfile model, forms, auth views & decorators
│   ├── forms.py                   # RegistrationForm, LoginForm, ProfileEditForm
│   ├── decorators.py              # @admin_required, @member_required
│   ├── views.py                   # register, login, logout, dashboard, profile, admin views
│   └── tests_auth.py              # Automated auth & role permission tests
│
├── catalog/                       # App: Genre, Artist, Song, SongArtist, SongGenre models
│   ├── views.py                   # Catalogue browsing and management views
│   ├── migrations/                # Includes optional Song audio-file migration
│   └── management/commands/       # Seed and credited playback sample commands
│
├── playlists/                     # App: Playlist and PlaylistSong models
├── profiles/                      # App: Favourite model, views, routes & ownership tests
│
├── templates/                     # Global Django templates
│   ├── base.html                  # Responsive layout with dynamic navigation
│   ├── index.html                 # Verification landing page
│   ├── accounts/                  # register, login, profile, dashboard, admin_dashboard, access_denied
│   ├── catalog/                   # browse, details & catalogue management
│   └── profiles/                  # My Favourites page and shared favourite control
│
├── static/                        # Static assets
│   ├── css/style.css              # Custom modern dark theme
│   └── js/                         # Fetch API favourites and shared HTML5 player
├── media/audio/                   # CC BY sample audio and attribution
│   ├── ATTRIBUTION.md
│   └── samples/                   # Five credited MP3 samples
│
├── docs/                          # Detailed architectural and design documentation
│   ├── PROJECT_OVERVIEW.md        # Concept, user personas, and project boundaries
│   ├── TECHNICAL_ARCHITECTURE.md  # Multi-tier system architecture breakdown
│   ├── DATABASE_DESIGN_PLAN.md    # Conceptual & logical relational schema plan
│   ├── DEVELOPMENT_ROADMAP.md     # 14-phase development roadmap
│   ├── AUTHENTICATION_AND_PERMISSIONS.md # Auth flow, roles & security model
│   └── database/                  # Comprehensive database documentation & ER diagram
│       ├── er_diagram.png         # High-resolution ER Diagram PNG
│       ├── er_diagram_source.mmd  # Mermaid ER diagram source
│       ├── relational_schema.md   # Relational schema specification
│       ├── constraints.md         # Database constraints specification
│       ├── normalization.md       # 1NF, 2NF, 3NF detailed report
│       ├── database_dictionary.md # Column-by-column data dictionary
│       └── SAMPLE_DATA_REPORT.md  # Live counts & demo accounts report
│
├── database/                      # Database utilities and schema inspection tools
│   ├── inspect_schema.py          # Script to inspect SQLite DDL & constraints
│   ├── verify_sample_data.py      # Script to verify record counts & foreign keys
│   └── capture_ui_snapshots.py    # UI snapshot generator
│
├── sql/                           # Academic SQL demonstration scripts
│   └── README.md
│
└── screenshots/                   # Academic verification screenshots & UI snapshots
    └── ui/                        # HTML snapshots of auth & dashboard pages
```

---

## 6. Installation & Quick Start Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14.7)
- Git
- DB Browser for SQLite

### Step-by-Step Setup Instructions

1. **Clone the repository and open the project folder**:
   ```bash
   git clone <repository-url>
   cd "MY PROJECT"
   ```

2. **Create a virtual environment**:
   - On **Windows**:
     ```powershell
     python -m venv .venv
     ```
   - On **macOS / Linux**:
     ```bash
     python3 -m venv .venv
     ```

3. **Activate the virtual environment**:
   - On **Windows**:
     ```powershell
     .\.venv\Scripts\activate
     ```
   - On **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Populate synthetic sample data**:
   ```bash
   python manage.py seed_data
   ```

7. **Load the credited playback samples** (the five MP3s are included in the repository under `media/audio/samples/`):
   ```bash
   python manage.py load_playback_samples
   ```
   This command is safe to repeat. Read `media/audio/ATTRIBUTION.md` before redistributing the audio files.

8. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

9. **Access the application**:
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### Deployment Configuration

For local development, the app defaults to `DEBUG=True` and generates a temporary development-only secret key when `DJANGO_SECRET_KEY` is unset. The `.env.example` file is a reference; Django does not load `.env` files automatically. Set the variables in the process environment before starting Django.

Before any public deployment, set `DJANGO_DEBUG=False`, provide a unique `DJANGO_SECRET_KEY`, and set `DJANGO_ALLOWED_HOSTS` to the exact hostnames. Production settings require the key and host list, reject wildcard hosts, redirect to HTTPS, and mark session and CSRF cookies secure. Set `DJANGO_SECURE_HSTS_SECONDS` to a positive duration only after HTTPS is confirmed for the production domain; enable HSTS subdomain or preload policies only when they are appropriate for every affected hostname. Do not deploy seeded demo accounts or run `seed_data` against a public deployment.

---

## 7. Evaluation Accounts

The local `seed_data` command creates synthetic administrator and member accounts for evaluation. These local-only accounts use predictable development passwords and must not be enabled in a public deployment. The application does not display their credentials on the login page.

For complete documentation, see [AUTHENTICATION_AND_PERMISSIONS.md](docs/AUTHENTICATION_AND_PERMISSIONS.md).

---

## 8. Current Progress

Phases 8–12 are complete. Phase 13 quality assurance is complete: 125 automated tests pass, the populated SQLite database passed integrity and foreign-key checks, and responsive browser checks at the requested viewport sizes found no horizontal overflow on the audited pages. See the [Phase 13 QA report](docs/PHASE_13_QA_REPORT.md) and its [final screenshots](screenshots/final/), as well as the [Phase 12 playback report](docs/PHASE_12_PLAYBACK_REPORT.md), [Phase 11 report](docs/PHASE_11_DBMS_REPORT.md), [SQL practical guide](docs/DBMS_SQL_PRACTICAL.md), [Phase 9 report](docs/PHASE_9_FAVOURITES_REPORT.md), and [Phase 10 report](docs/PHASE_10_PLAYLISTS_REPORT.md).
