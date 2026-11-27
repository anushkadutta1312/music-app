# Project Overview: Music App

## 1. Executive Summary

**Music App** is a responsive, database-driven full stack web application engineered for music discovery, catalogue browsing, and personal playlist management.

The platform provides users with an intuitive, modern interface to explore songs, artists, and genres, maintain a curated list of favourite tracks, and create custom playlists. Audio playback is facilitated via an external music provider integration (e.g. YouTube official embeds or Jamendo API), avoiding the requirement to host copyrighted media files.

Engineered specifically for academic evaluation in **Database Management Systems (DBMS)** and **Full Stack Web Development**, the project demonstrates clean software architecture, relational database normalization (1NF, 2NF, 3NF), relational constraints, server-side access control, and direct SQL practical querying.

---

## 2. Target User Personas

1. **Music Member (Authenticated User)**
   - Registers for a personal account and logs in securely.
   - Explores the music dashboard featuring recent tracks, genres, and featured artists.
   - Browses and searches songs by title, artist, or genre.
   - Plays audio previews via the integrated external player.
   - Adds/removes tracks to/from their personal **Favourites**.
   - Creates, views, renames, edits, and deletes personal **Playlists**, and manages playlist track ordering.

2. **Music Administrator / Staff (`ADMIN`)**
   - Manages the core music catalogue (adding/editing artists, songs, and genres).
   - Oversees database integrity and monitors system records.

3. **Anonymous Guest**
   - Can access the landing page, browse general platform information, and register/login.
   - Protected actions (favouriting, playlist management) require authentication.

---

## 3. Approved Functional Scope (In-Scope)

- **User Authentication**:
  - Secure registration, login, session management, and logout using Django authentication.
  - Password hashing (PBKDF2) and input sanitization.
  - Basic profile information.
- **Music Dashboard**:
  - Recently added songs from the database.
  - Popular songs based on actual database metrics (e.g., most favourited / most added to playlists).
  - Visual genre cards and featured artist cards.
  - Quick-access overview of the user's personal playlists and favourites.
- **Music Catalogue**:
  - Comprehensive song browsing with metadata (title, artist, genre, duration, release year).
  - Artist profile pages listing their songs.
  - Genre-based filtering and catalogue sorting.
  - Pagination for large result sets.
- **Music Playback**:
  - External music provider integration (e.g., YouTube official embed player or Jamendo API stream).
  - Storage of provider track identifiers/metadata rather than raw audio files.
- **Favourite Songs**:
  - Add to favourites, view favourites list, and remove from favourites.
  - Database-enforced uniqueness preventing duplicate favourites.
  - Server-side isolation ensuring users only manage their own favourites.
- **Playlist Management (Full CRUD)**:
  - Create playlists with title and description.
  - View personal playlists and playlist detail views.
  - Update/rename playlist metadata.
  - Add and remove songs with custom track ordering (`track_order`).
  - Delete playlists.
  - Strict server-side ownership authorization.
- **Search & Asynchronous Interactions**:
  - Keyword search across songs, artists, and genres.
  - Dynamic, asynchronous search using JavaScript Fetch API without full page reload.

---

## 4. Boundaries & Explicit Exclusions (Strictly Out-of-Scope)

To maintain focus on core academic database objectives and prevent unnecessary complexity, the following features are **strictly excluded**:

- ❌ **No Social Networking**: No social feeds, timelines, or user wall posts.
- ❌ **No Chat or Direct Messaging**: No user-to-user messaging, chatrooms, or conversation threads.
- ❌ **No Social Connections**: No friend requests, followers, following, or user connections.
- ❌ **No Algorithmic / AI Recommendations**: No machine learning, similarity matching, or automated user matching.
- ❌ **No Messaging Notifications**: No notification tickers or message alerts.
- ❌ **No Heavy SPA Frameworks**: Powered by clean Django templates, CSS3, and Vanilla JavaScript (Fetch API).

---

## 5. Academic Alignment

The application fulfills all formal DBMS and Full Stack requirements:
- Minimum 6 application tables (10 proposed: User, UserProfile, Artist, Genre, Song, SongArtist, SongGenre, Favourite, Playlist, PlaylistSong).
- Primary keys, foreign keys, UNIQUE, NOT NULL, DEFAULT, and CHECK constraints.
- Normalization adhering strictly to 1NF, 2NF, and 3NF.
- Two distinct user roles (`ADMIN` and `MEMBER`) with server-side access controls.
- 12+ SQL demonstration queries covering DDL, DML, joins, aggregations, and subqueries executed against `db.sqlite3`.
