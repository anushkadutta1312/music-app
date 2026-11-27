(() => {
    const csrfToken = () => {
        const cookie = document.cookie
            .split('; ')
            .find((item) => item.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
    };

    document.addEventListener('submit', async (event) => {
        const form = event.target.closest('[data-favourite-form]');
        if (!form) return;

        event.preventDefault();
        const button = form.querySelector('[data-favourite-button]');
        const feedback = form.querySelector('[data-favourite-feedback]');
        const actionInput = form.querySelector('input[name="action"]');
        if (!button || !actionInput) return;

        button.disabled = true;
        form.setAttribute('aria-busy', 'true');
        if (feedback) feedback.textContent = 'Saving…';

        try {
            // An input named "action" shadows HTMLFormElement.action in some browsers.
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
                throw new Error(result.error || 'Could not update favourites.');
            }

            const isFavourited = result.is_favourited;
            actionInput.value = isFavourited ? 'remove' : 'add';
            button.setAttribute('aria-pressed', String(isFavourited));
            button.textContent = isFavourited ? '♥ Remove from favourites' : '♡ Add to favourites';
            button.classList.toggle('btn-primary', !isFavourited);
            button.classList.toggle('btn-secondary', isFavourited);
            if (feedback) feedback.textContent = result.message;
            if (!isFavourited && form.dataset.removeCardOnUnsave === 'true') {
                const card = form.closest('.song-card');
                const grid = form.closest('[data-favourites-grid]');
                const pageFeedback = document.querySelector('[data-favourites-page-feedback]');
                if (pageFeedback) pageFeedback.textContent = result.message;
                if (card) card.remove();
                if (grid && !grid.querySelector('.song-card')) {
                    grid.hidden = true;
                    const emptyState = document.querySelector('[data-favourites-empty]');
                    if (emptyState) emptyState.hidden = false;
                }
            }
        } catch (error) {
            if (feedback) feedback.textContent = error.message || 'Could not update favourites. Please try again.';
        } finally {
            button.disabled = false;
            form.removeAttribute('aria-busy');
        }
    });
})();
