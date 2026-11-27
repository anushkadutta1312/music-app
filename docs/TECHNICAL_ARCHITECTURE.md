# Technical Architecture Specification

## 1. Architectural Overview

The **Music App** is built upon the classic **Model-View-Template (MVT)** architectural pattern provided by Django, backed by a normalized SQLite database and an accessible, responsive Vanilla JavaScript frontend.

```
+-------------------------------------------------------------------+
|                        Client Layer                               |
|        HTML5  •  CSS3  •  Vanilla JavaScript  •  Fetch API        |
+-------------------------------------------------------------------+
                                  │
                                  │  HTTP / HTTPS Requests
                                  │  (Form Submissions, Asynchronous Fetch API)
                                  ▼
+-------------------------------------------------------------------+
|                     Application Layer (Django)                    |
|   ┌───────────────────────────────────────────────────────────┐   |
|   │ URL Dispatcher & Middleware (CSRF, Auth Sessions)         │   |
|   ├───────────────────────────────────────────────────────────┤   |
|   │ Views (Function-Based / Class-Based Views)                │   |
|   │   • accounts: registration, login, logout, role check     │   |
|   │   • catalog: song/artist browsing, genre filter, search   │   |
|   │   • playlists: playlist CRUD, track order management      │   |
|   │   • profiles: user profile, favourite songs               │   |
|   ├───────────────────────────────────────────────────────────┤   |
|   │ Forms & ModelForms (Server-side validation & cleaning)    │   |
|   ├───────────────────────────────────────────────────────────┤   |
|   │ Templates (Server-rendered HTML with Django Template Lang)│   |
|   └───────────────────────────────────────────────────────────┘   |
+-------------------------------------------------------------------+
                                  │
                                  │  Python Objects / ORM API
                                  ▼
+-------------------------------------------------------------------+
|                     Persistence Layer (Django ORM)                |
|            Django Object-Relational Mapping (ORM) Engine          |
+-------------------------------------------------------------------+
                                  │
                                  │  Compiled SQL Queries
                                  ▼
+-------------------------------------------------------------------+
|                     Database Layer (SQLite 3)                     |
|                         db.sqlite3                                |
|  (10 Tables, PKs, FKs, Unique, Not Null, Default, Check)          |
+-------------------------------------------------------------------+
                                  │
                                  │  Inspection / Academic SQL Verification
                                  ▼
+-------------------------------------------------------------------+
|                   DB Browser for SQLite Tool                      |
+-------------------------------------------------------------------+
```

---

## 2. External Music Provider Architecture

To support music playback without hosting copyrighted audio files on our server:
- The `Song` entity stores metadata and an external reference identifier (e.g. YouTube Video ID or Jamendo Track ID).
- When a user clicks play, the client layer triggers playback via the external provider's official embedded player or audio stream.
- No copyrighted MP3/audio files are stored on disk or served by Django.

---

## 3. Role-Based Access Control (RBAC)

The system enforces two distinct roles:

1. **`ADMIN` (Staff / Superuser)**:
   - Full catalogue management permissions.
   - Can create, update, and delete artists, genres, and songs.
   - Access to Django administration interface.
2. **`MEMBER` (Standard Authenticated User)**:
   - Can manage their own profile.
   - Can add/remove songs from their own favourites.
   - Can create, edit, manage songs in, and delete their own playlists.
   - Cannot mutate other users' playlists or modify catalogue entities.

---

## 4. Security & Data Integrity

1. **CSRF Protection**: All state-modifying requests (POST, PUT, DELETE) require a valid CSRF token (`{% csrf_token %}`).
2. **Password Security**: Passwords hashed using Django's built-in PBKDF2 with SHA-256 algorithm.
3. **Server-Side Authorization**: Every view handler verifies user ownership before permitting data updates or deletions (preventing Insecure Direct Object References).
4. **SQL Injection Defense**: All database operations use Django ORM parameterized queries.
5. **XSS Defense**: Django template variables are escaped automatically by default.
