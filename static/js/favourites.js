(() => {
    const csrfToken = () => {
        const cookie = document.cookie
            .split('; ')
            .find((item) => item.startsWith('csrftoken='));
        return cookie ? decodeURIComponent(cookie.slice('csrftoken='.length)) : '';
    };

    const showToast = (message, isFavourited) => {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'fixed bottom-28 right-8 z-50 flex flex-col gap-2.5 pointer-events-none select-none';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = 'pointer-events-auto bg-[#181a22]/95 backdrop-blur-md text-white border border-white/10 px-4 py-3 rounded-2xl shadow-2xl flex items-center gap-3 text-xs font-semibold transform transition-all duration-300 translate-y-3 opacity-0';
        toast.innerHTML = `
            <div class="w-8 h-8 rounded-xl ${isFavourited ? 'bg-rose-500/15 text-rose-400 border border-rose-500/20' : 'bg-white/5 text-slate-400 border border-white/10'} flex items-center justify-center shrink-0 shadow-inner">
                <iconify-icon icon="lucide:heart" class="text-base ${isFavourited ? 'fill-rose-500 text-rose-500' : 'text-slate-400'}"></iconify-icon>
            </div>
            <div class="flex flex-col">
                <span class="text-white">${message}</span>
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
        }, 2200);
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
            button.title = isFavourited ? 'Remove from favourites' : 'Add to favourites';

            // Keep clean icon without changing button dimensions or adding wide text
            if (isFavourited) {
                button.className = 'p-2 rounded-xl text-rose-500 hover:text-rose-400 hover:bg-rose-500/10 transition-all focus:outline-none';
                button.innerHTML = '<iconify-icon icon="lucide:heart" class="text-lg fill-rose-500 text-rose-500 block"></iconify-icon>';
            } else {
                button.className = 'p-2 rounded-xl text-slate-500 hover:text-rose-500 hover:bg-white/5 transition-all focus:outline-none';
                button.innerHTML = '<iconify-icon icon="lucide:heart" class="text-lg text-slate-400 hover:text-rose-400 block"></iconify-icon>';
            }

            if (feedback) feedback.textContent = result.message;
            showToast(result.message || (isFavourited ? 'Song added to favourites' : 'Song removed from favourites'), isFavourited);

            // If on favourites page with remove-card flag, smoothly remove the row/card
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
            if (feedback) feedback.textContent = error.message;
        } finally {
            button.disabled = false;
            form.removeAttribute('aria-busy');
        }
    });
})();
