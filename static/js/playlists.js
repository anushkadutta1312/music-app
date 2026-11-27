(() => {
    const csrfToken = () => {
        const cookie = document.cookie
            .split('; ')
            .find((item) => item.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
    };

    const announce = (form, message) => {
        const local = form.querySelector('[data-playlist-feedback]');
        const page = document.querySelector('[data-playlist-page-feedback]');
        if (local) local.textContent = message;
        if (page) page.textContent = message;
    };

    const updateTrackList = (positions) => {
        const list = document.querySelector('[data-playlist-track-list]');
        if (!list || !Array.isArray(positions)) return;
        const rows = new Map(Array.from(list.querySelectorAll('[data-playlist-track]'))
            .map((row) => [Number(row.dataset.songId), row]));
        positions.forEach(({song_id, position}, index) => {
            const row = rows.get(Number(song_id));
            if (!row) return;
            row.querySelector('[data-track-position]').textContent = String(position);
            const moveButtons = row.querySelectorAll('[data-track-move] button');
            if (moveButtons[0]) moveButtons[0].disabled = index === 0;
            if (moveButtons[1]) moveButtons[1].disabled = index === positions.length - 1;
            list.appendChild(row);
        });
        const count = document.querySelector('[data-playlist-song-count]');
        if (count) count.textContent = String(positions.length);
        const empty = document.querySelector('[data-playlist-empty]');
        if (empty) empty.hidden = positions.length !== 0;
    };

    document.addEventListener('submit', async (event) => {
        const form = event.target.closest('[data-playlist-form]');
        if (!form) return;
        event.preventDefault();

        const button = form.querySelector('button[type="submit"]');
        let updated = false;
        if (button) button.disabled = true;
        form.setAttribute('aria-busy', 'true');

        try {
            const response = await fetch(form.getAttribute('action'), {
                method: 'POST',
                body: new FormData(form),
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': csrfToken(),
                },
            });
            const result = await response.json();
            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Could not update the playlist.');
            }

            announce(form, result.message);
            updated = true;
            if (form.hasAttribute('data-track-remove')) {
                const row = form.closest('[data-playlist-track]');
                if (row) row.remove();
            }
            if (result.positions) updateTrackList(result.positions);
        } catch (error) {
            announce(form, error.message || 'Could not update the playlist. Please try again.');
        } finally {
            form.removeAttribute('aria-busy');
            if (button && button.isConnected) {
                // Move buttons are recalculated after the request, including edge positions.
                if (!form.hasAttribute('data-track-move') || !updated) button.disabled = false;
            }
        }
    });
})();
