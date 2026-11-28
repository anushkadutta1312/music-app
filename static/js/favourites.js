(() => {
    const csrfToken = () => {
        const cookie = document.cookie
            .split('; ')
            .find((item) => item.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
    };

    const filledHeartSvg = '<svg class="w-5 h-5 text-rose-500 fill-current block pointer-events-none" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>';

    const outlineHeartSvg = '<svg class="w-5 h-5 text-slate-400 hover:text-rose-400 block pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>';

    const showToast = (message, isFavourited) => {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed top-4 left-4 right-4 sm:left-auto sm:right-6 md:bottom-28 md:top-auto md:right-8 z-[9999] flex flex-col gap-2.5 pointer-events-none select-none';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = 'pointer-events-auto bg-[#181a22] text-white border border-white/10 px-5 py-3.5 rounded-2xl shadow-2xl flex items-center gap-3.5 text-xs font-semibold transform transition-all duration-300 translate-y-3 opacity-0 backdrop-blur-xl';
        toast.innerHTML = `
            <div class="w-8 h-8 rounded-xl ${isFavourited ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-white/10 text-slate-400 border border-white/10'} flex items-center justify-center shrink-0 shadow-lg">
                ${isFavourited ? '<svg class="w-4 h-4 text-rose-500 fill-current" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>' : '<svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>'}
            </div>
            <div class="flex flex-col">
                <span class="text-white font-bold text-xs">${message}</span>
                <span class="text-[10px] text-slate-400 font-normal">${isFavourited ? 'Saved to Your Favourites' : 'Removed from Your Favourites'}</span>
            </div>
        `;
        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-3', 'opacity-0');
            toast.classList.add('translate-y-0', 'opacity-100');
        });

        setTimeout(() => {
            toast.classList.remove('opacity-100');
            toast.classList.add('opacity-0', 'translate-y-2');
            setTimeout(() => toast.remove(), 350);
        }, 2400);
    };

    document.addEventListener('submit', async (event) => {
        const form = event.target.closest('[data-favourite-form]');
        if (!form) return;

        event.preventDefault();
        event.stopImmediatePropagation();

        const button = form.querySelector('[data-favourite-button]');
        const actionInput = form.querySelector('input[name="action"]');
        if (!button || !actionInput) return;

        button.disabled = true;
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
                throw new Error(result.error || 'Could not update favourites.');
            }

            const isFavourited = result.is_favourited;
            actionInput.value = isFavourited ? 'remove' : 'add';
            button.setAttribute('aria-pressed', String(isFavourited));
            button.setAttribute('aria-label', isFavourited ? 'Remove from favourites' : 'Add to favourites');
            button.title = isFavourited ? 'Remove from favourites' : 'Add to favourites';

            if (isFavourited) {
                button.className = 'p-2 rounded-xl text-rose-500 hover:text-rose-400 hover:bg-rose-500/10 transition-all focus:outline-none';
                button.innerHTML = filledHeartSvg;
            } else {
                button.className = 'p-2 rounded-xl text-slate-500 hover:text-rose-500 hover:bg-white/5 transition-all focus:outline-none';
                button.innerHTML = outlineHeartSvg;
            }

            showToast(result.message || (isFavourited ? 'Song added to favourites' : 'Song removed from favourites'), isFavourited);

            if (!isFavourited && form.dataset.removeCardOnUnsave === 'true') {
                const card = form.closest('.song-card') || form.closest('.group');
                const grid = form.closest('[data-favourites-grid]');
                if (card) {
                    card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        card.remove();
                        if (grid && !grid.querySelector('[data-favourite-form]')) {
                            grid.hidden = true;
                            const emptyState = document.querySelector('[data-favourites-empty]');
                            if (emptyState) emptyState.hidden = false;
                        }
                    }, 300);
                }
            }
        } catch (error) {
            showToast(error.message || 'Could not update favourites. Please try again.', false);
        } finally {
            button.disabled = false;
            form.removeAttribute('aria-busy');
        }
    }, true);
})();
