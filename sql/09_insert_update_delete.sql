-- Queries 13–15 — Demonstrate INSERT, UPDATE, and DELETE safely.
-- Run all statements in this file as one unit. The SAVEPOINT is rolled back at
-- the end, so the temporary artist never remains in the project's database.
-- If you execute statement-by-statement in DB Browser, execute ROLLBACK TO and
-- RELEASE before closing; do not click Write Changes before rollback.

SAVEPOINT phase11_sql_demo;

-- Query 13 — INSERT a uniquely named, clearly temporary demonstration artist.
INSERT INTO catalog_artist
    (name, biography, image_url, external_provider, external_artist_id, created_at, updated_at)
VALUES
    ('__PHASE11_SQL_DEMO__', 'Temporary SQL practical record; safe to roll back.', '', '', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

SELECT id, name, biography
FROM catalog_artist
WHERE name = '__PHASE11_SQL_DEMO__';

-- Query 14 — UPDATE only that uniquely identifiable temporary artist.
UPDATE catalog_artist
SET biography = 'Updated temporarily to demonstrate SQL UPDATE.'
WHERE name = '__PHASE11_SQL_DEMO__';

SELECT id, name, biography
FROM catalog_artist
WHERE name = '__PHASE11_SQL_DEMO__';

-- Query 15 — DELETE only the same temporary artist, then prove it is absent.
DELETE FROM catalog_artist
WHERE name = '__PHASE11_SQL_DEMO__';

SELECT COUNT(*) AS temporary_rows_after_delete
FROM catalog_artist
WHERE name = '__PHASE11_SQL_DEMO__';

-- Undo the temporary insert/update/delete so database contents stay unchanged.
ROLLBACK TO phase11_sql_demo;
RELEASE phase11_sql_demo;
