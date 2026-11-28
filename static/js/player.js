(function () {
    'use strict';

    const player = document.querySelector('[data-site-player]');
    const audio = document.querySelector('[data-audio-player]');
    if (!player || !audio) return;

    const controls = {
        previous: player.querySelector('[data-player-previous]'),
        toggle: player.querySelector('[data-player-toggle]'),
        next: player.querySelector('[data-player-next]'),
        seek: player.querySelector('[data-player-seek]'),
        currentTime: player.querySelector('[data-player-current-time]'),
        duration: player.querySelector('[data-player-duration]'),
        status: player.querySelector('[data-player-status]'),
        title: player.querySelector('[data-player-title]'),
        artist: player.querySelector('[data-player-artist]'),
        artwork: player.querySelector('[data-player-artwork]'),
        artworkFallback: player.querySelector('[data-player-artwork-fallback]'),
        volume: player.querySelector('[data-player-volume]'),
        mute: player.querySelector('[data-player-mute]'),
    };

    const fsModal = document.getElementById('fullscreen-player-modal');
    const fsClose = document.getElementById('close-fullscreen-player-btn');
    const fsControls = {
        title: document.querySelector('[data-fs-title]'),
        artist: document.querySelector('[data-fs-artist]'),
        album: document.querySelector('[data-fs-album]'),
        artwork: document.querySelector('[data-fs-artwork]'),
        artworkFallback: document.querySelector('[data-fs-artwork-fallback]'),
        currentTime: document.querySelector('[data-fs-current-time]'),
        duration: document.querySelector('[data-fs-duration]'),
        seek: document.querySelector('[data-fs-seek]'),
        toggle: document.querySelector('[data-fs-toggle]'),
        previous: document.querySelector('[data-fs-previous]'),
        next: document.querySelector('[data-fs-next]'),
    };

    let queue = [];
    let currentIndex = -1;
    let lastAudibleVolume = 0.8;

    function formatTime(value) {
        if (!Number.isFinite(value) || value < 0) return '0:00';
        const seconds = Math.floor(value);
        return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    }

    function setStatus(message, state) {
        if (controls.status) controls.status.textContent = message;
        player.dataset.playerState = state;
    }

    function getLiveElements() {
        return {
            titles: document.querySelectorAll('[data-live-title]'),
            artists: document.querySelectorAll('[data-live-artist]'),
            artworks: document.querySelectorAll('[data-live-artwork]'),
            currentTimes: document.querySelectorAll('[data-live-current-time]'),
            durations: document.querySelectorAll('[data-live-duration]'),
            progressBars: document.querySelectorAll('[data-live-progress]'),
            toggles: document.querySelectorAll('[data-live-toggle]'),
            previousBtns: document.querySelectorAll('[data-live-previous]'),
            nextBtns: document.querySelectorAll('[data-live-next]'),
        };
    }

    function updateLiveTrack(track) {
        if (!track) return;
        const live = getLiveElements();
        live.titles.forEach(el => el.textContent = track.title);
        live.artists.forEach(el => el.textContent = track.artist || track.album || 'Unknown artist');
        live.artworks.forEach(el => {
            if (track.cover) {
                el.src = track.cover;
                el.style.display = '';
            }
        });
        live.currentTimes.forEach(el => el.textContent = '0:00');
        live.durations.forEach(el => el.textContent = '0:00');
        live.progressBars.forEach(el => el.style.width = '0%');

        if (fsControls.title) fsControls.title.textContent = track.title;
        if (fsControls.artist) fsControls.artist.textContent = track.artist || track.album || 'Unknown artist';
        if (fsControls.album) fsControls.album.textContent = track.album || 'Groovy Collection';
        if (fsControls.artwork) {
            if (track.cover) {
                fsControls.artwork.src = track.cover;
                fsControls.artwork.hidden = false;
                if (fsControls.artworkFallback) fsControls.artworkFallback.hidden = true;
            } else {
                fsControls.artwork.hidden = true;
                if (fsControls.artworkFallback) fsControls.artworkFallback.hidden = false;
            }
        }
        if (fsControls.currentTime) fsControls.currentTime.textContent = '0:00';
        if (fsControls.duration) fsControls.duration.textContent = '0:00';
        if (fsControls.seek) {
            fsControls.seek.value = '0';
            fsControls.seek.disabled = true;
        }
    }

    function updateLiveTime() {
        const live = getLiveElements();
        const currentStr = formatTime(audio.currentTime);
        const durationStr = formatTime(audio.duration);
        live.currentTimes.forEach(el => el.textContent = currentStr);
        if (fsControls.currentTime) fsControls.currentTime.textContent = currentStr;

        if (Number.isFinite(audio.duration) && audio.duration > 0) {
            live.durations.forEach(el => el.textContent = durationStr);
            if (fsControls.duration) fsControls.duration.textContent = durationStr;

            const pct = Math.min(100, Math.max(0, (audio.currentTime / audio.duration) * 100));
            live.progressBars.forEach(el => el.style.width = `${pct}%`);
            if (controls.seek) {
                controls.seek.style.background = `linear-gradient(to right, #6366f1 0%, #8b5cf6 ${pct}%, rgba(255,255,255,0.12) ${pct}%, rgba(255,255,255,0.12) 100%)`;
            }
            if (fsControls.seek) {
                fsControls.seek.disabled = false;
                fsControls.seek.value = String(Math.round((audio.currentTime / audio.duration) * 1000));
                fsControls.seek.style.background = `linear-gradient(to right, #6366f1 0%, #8b5cf6 ${pct}%, rgba(255,255,255,0.15) ${pct}%, rgba(255,255,255,0.15) 100%)`;
            }
        }
    }

    function updatePlayStateUI(isPlaying) {
        if (controls.toggle) {
            controls.toggle.innerHTML = isPlaying
                ? '<iconify-icon icon="lucide:pause" class="text-xl"></iconify-icon>'
                : '<iconify-icon icon="lucide:play" class="text-xl ml-0.5"></iconify-icon>';
            controls.toggle.setAttribute('aria-label', isPlaying ? 'Pause' : 'Play');
        }

        const live = getLiveElements();
        live.toggles.forEach(btn => {
            btn.innerHTML = isPlaying
                ? '<iconify-icon icon="lucide:pause" class="text-2xl"></iconify-icon>'
                : '<iconify-icon icon="lucide:play" class="text-2xl ml-0.5"></iconify-icon>';
            btn.setAttribute('aria-label', isPlaying ? 'Pause' : 'Play');
        });

        if (fsControls.toggle) {
            fsControls.toggle.innerHTML = isPlaying
                ? '<iconify-icon icon="lucide:pause" class="text-3xl text-black"></iconify-icon>'
                : '<iconify-icon icon="lucide:play" class="text-3xl ml-1 text-black"></iconify-icon>';
            fsControls.toggle.setAttribute('aria-label', isPlaying ? 'Pause' : 'Play');
        }
    }

    function updateNavigation() {
        const active = currentIndex >= 0 && queue.length > 0;
        if (controls.previous) controls.previous.disabled = !active || currentIndex <= 0;
        if (controls.next) controls.next.disabled = !active || currentIndex >= queue.length - 1;
        if (controls.toggle) controls.toggle.disabled = !active;
        if (controls.volume) controls.volume.disabled = !active;
        if (controls.mute) controls.mute.disabled = !active;

        const live = getLiveElements();
        live.previousBtns.forEach(btn => { btn.disabled = !active || currentIndex <= 0; });
        live.nextBtns.forEach(btn => { btn.disabled = !active || currentIndex >= queue.length - 1; });

        if (fsControls.previous) fsControls.previous.disabled = !active || currentIndex <= 0;
        if (fsControls.next) fsControls.next.disabled = !active || currentIndex >= queue.length - 1;
        if (fsControls.toggle) fsControls.toggle.disabled = !active;
    }

    function readQueue(container) {
        let queueScope = container || document;
        let buttons = Array.from(queueScope.querySelectorAll('[data-player-track]'));
        if (!buttons.length) {
            buttons = Array.from(document.querySelectorAll('[data-player-track]'));
        }
        return buttons
            .map((button) => ({
                src: (button.dataset.audioUrl || '').trim(),
                title: button.dataset.trackTitle || 'Untitled track',
                artist: button.dataset.trackArtist || 'Unknown artist',
                album: button.dataset.trackAlbum || '',
                cover: button.dataset.trackCover || '',
            }))
            .filter((track) => Boolean(track.src));
    }

    function updateArtwork(url) {
        if (!controls.artwork) return;
        controls.artwork.onerror = () => {
            controls.artwork.hidden = true;
            if (controls.artworkFallback) controls.artworkFallback.hidden = false;
        };
        if (url) {
            controls.artwork.src = url;
            controls.artwork.hidden = false;
            if (controls.artworkFallback) controls.artworkFallback.hidden = true;
        } else {
            controls.artwork.removeAttribute('src');
            controls.artwork.hidden = true;
            if (controls.artworkFallback) controls.artworkFallback.hidden = false;
        }
    }

    function playCurrentTrack(shouldPlay) {
        const track = queue[currentIndex];
        if (!track) return;

        audio.pause();
        audio.src = track.src;
        audio.load();
        
        if (controls.title) controls.title.textContent = track.title;
        if (controls.artist) controls.artist.textContent = track.artist || track.album || 'Unknown artist';
        if (controls.currentTime) controls.currentTime.textContent = '0:00';
        if (controls.duration) controls.duration.textContent = '0:00';
        if (controls.seek) {
            controls.seek.value = '0';
            controls.seek.disabled = true;
        }
        
        updateArtwork(track.cover);
        updateLiveTrack(track);
        updateNavigation();
        updatePlayStateUI(shouldPlay);
        setStatus(`Loading ${track.title}…`, 'loading');

        if (shouldPlay) {
            audio.play().catch((error) => {
                const message = error && error.name === 'NotAllowedError'
                    ? 'Playback was blocked by the browser. Press Play to try again.'
                    : 'This audio file could not be played. Try another track.';
                setStatus(message, 'error');
                updatePlayStateUI(false);
            });
        }
    }

    function startFrom(container, clickedButton, playAll) {
        queue = readQueue(container);
        if (!queue.length) {
            queue = readQueue(document);
        }

        if (!queue.length) {
            setStatus('There are no available audio files in this playlist.', 'unavailable');
            currentIndex = -1;
            updateNavigation();
            return;
        }

        if (playAll) {
            // Find the first track with audio available
            currentIndex = queue.findIndex(track => Boolean(track.src));
            if (currentIndex < 0) currentIndex = 0;
        } else if (clickedButton) {
            const target = (clickedButton.dataset.audioUrl || '').trim();
            currentIndex = queue.findIndex((track) => track.src === target);
            if (currentIndex < 0) {
                queue = readQueue(document);
                currentIndex = queue.findIndex((track) => track.src === target);
            }
        }

        if (currentIndex < 0 || currentIndex >= queue.length) {
            setStatus('This audio file is unavailable. Choose another track.', 'unavailable');
            updateNavigation();
            return;
        }
        playCurrentTrack(true);
    }

    // Global click delegate for track buttons, play-all, and live widgets
    document.addEventListener('click', (event) => {
        const playAllButton = event.target.closest('[data-player-play-all]');
        if (playAllButton) {
            // Find all playable tracks on page
            startFrom(document, null, true);
            return;
        }

        const trackButton = event.target.closest('[data-player-track]');
        if (trackButton) {
            const container = trackButton.closest('[data-player-queue]') || document;
            startFrom(container, trackButton, false);
            return;
        }

        const liveToggle = event.target.closest('[data-live-toggle]');
        if (liveToggle) {
            if (audio.src && audio.src !== window.location.href) {
                if (audio.paused) {
                    audio.play().catch(() => setStatus('Could not play track.', 'error'));
                } else {
                    audio.pause();
                }
            } else {
                // If not started yet, play first available track in document
                queue = readQueue(document);
                if (queue.length > 0) {
                    currentIndex = 0;
                    playCurrentTrack(true);
                }
            }
            return;
        }

        const livePrev = event.target.closest('[data-live-previous]');
        if (livePrev) {
            if (currentIndex > 0) {
                currentIndex -= 1;
                playCurrentTrack(true);
            }
            return;
        }

        const liveNext = event.target.closest('[data-live-next]');
        if (liveNext) {
            if (currentIndex >= 0 && currentIndex < queue.length - 1) {
                currentIndex += 1;
                playCurrentTrack(true);
            }
            return;
        }

        const liveSeek = event.target.closest('[data-live-seek]');
        if (liveSeek && Number.isFinite(audio.duration) && audio.duration > 0) {
            const rect = liveSeek.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const ratio = Math.max(0, Math.min(1, clickX / rect.width));
            audio.currentTime = ratio * audio.duration;
            updateLiveTime();
        }
    });

    if (controls.toggle) {
        controls.toggle.addEventListener('click', () => {
            if (audio.src && audio.src !== window.location.href) {
                if (audio.paused) {
                    audio.play().catch(() => setStatus('This audio file could not be played. Try another track.', 'error'));
                } else {
                    audio.pause();
                }
            } else {
                queue = readQueue(document);
                if (queue.length > 0) {
                    currentIndex = 0;
                    playCurrentTrack(true);
                }
            }
        });
    }

    if (controls.previous) {
        controls.previous.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex -= 1;
                playCurrentTrack(true);
            }
        });
    }

    if (controls.next) {
        controls.next.addEventListener('click', () => {
            if (currentIndex >= 0 && currentIndex < queue.length - 1) {
                currentIndex += 1;
                playCurrentTrack(true);
            }
        });
    }

    if (controls.seek) {
        controls.seek.addEventListener('input', () => {
            if (Number.isFinite(audio.duration) && audio.duration > 0) {
                audio.currentTime = (Number(controls.seek.value) / Number(controls.seek.max)) * audio.duration;
                updateLiveTime();
            }
        });
    }

    if (controls.volume) {
        controls.volume.addEventListener('input', () => {
            audio.volume = Number(controls.volume.value);
            audio.muted = audio.volume === 0;
            if (audio.volume > 0) lastAudibleVolume = audio.volume;
            if (controls.mute) {
                controls.mute.innerHTML = audio.muted
                    ? '<iconify-icon icon="lucide:volume-x" class="text-lg"></iconify-icon>'
                    : '<iconify-icon icon="lucide:volume-2" class="text-lg"></iconify-icon>';
            }
        });
    }

    if (controls.mute) {
        controls.mute.addEventListener('click', () => {
            if (audio.muted || audio.volume === 0) {
                audio.muted = false;
                audio.volume = lastAudibleVolume || 0.8;
                if (controls.volume) controls.volume.value = String(audio.volume);
            } else {
                lastAudibleVolume = audio.volume;
                audio.muted = true;
            }
            controls.mute.innerHTML = audio.muted
                ? '<iconify-icon icon="lucide:volume-x" class="text-lg"></iconify-icon>'
                : '<iconify-icon icon="lucide:volume-2" class="text-lg"></iconify-icon>';
        });
    }

    audio.addEventListener('loadstart', () => setStatus('Loading audio…', 'loading'));
    audio.addEventListener('canplay', () => {
        if (controls.seek) {
            controls.seek.disabled = false;
            controls.seek.max = '1000';
        }
        if (audio.paused) setStatus('Ready to play', 'paused');
    });
    audio.addEventListener('loadedmetadata', () => {
        if (controls.duration) controls.duration.textContent = formatTime(audio.duration);
        updateLiveTime();
    });
    audio.addEventListener('timeupdate', () => {
        if (controls.currentTime) controls.currentTime.textContent = formatTime(audio.currentTime);
        if (controls.duration) controls.duration.textContent = formatTime(audio.duration);
        if (controls.seek && Number.isFinite(audio.duration) && audio.duration > 0) {
            controls.seek.value = String(Math.round((audio.currentTime / audio.duration) * 1000));
        }
        updateLiveTime();
    });
    audio.addEventListener('play', () => {
        updatePlayStateUI(true);
    });
    audio.addEventListener('playing', () => {
        setStatus(`Playing ${controls.title ? controls.title.textContent : ''}`, 'playing');
        updatePlayStateUI(true);
    });
    audio.addEventListener('pause', () => {
        if (!audio.ended && audio.src) {
            updatePlayStateUI(false);
            setStatus(`Paused ${controls.title ? controls.title.textContent : ''}`, 'paused');
        }
    });
    audio.addEventListener('ended', () => {
        if (currentIndex < queue.length - 1) {
            currentIndex += 1;
            playCurrentTrack(true);
        } else {
            updatePlayStateUI(false);
            setStatus('Playback finished.', 'ended');
        }
    });
    audio.addEventListener('error', () => {
        if (controls.seek) controls.seek.disabled = true;
        setStatus('Audio sample could not be loaded. Skipping to next playable track…', 'error');
        if (currentIndex >= 0 && currentIndex < queue.length - 1) {
            currentIndex += 1;
            setTimeout(() => playCurrentTrack(true), 500);
        } else {
            updatePlayStateUI(false);
        }
    });

    if (controls.volume) audio.volume = Number(controls.volume.value);

    // Full-Screen Player Event Handlers
    if (fsControls.seek) {
        fsControls.seek.addEventListener('input', () => {
            if (!Number.isFinite(audio.duration) || audio.duration <= 0) return;
            const targetTime = (Number(fsControls.seek.value) / 1000) * audio.duration;
            if (fsControls.currentTime) fsControls.currentTime.textContent = formatTime(targetTime);
        });
        fsControls.seek.addEventListener('change', () => {
            if (!Number.isFinite(audio.duration) || audio.duration <= 0) return;
            audio.currentTime = (Number(fsControls.seek.value) / 1000) * audio.duration;
        });
    }

    if (fsControls.toggle) {
        fsControls.toggle.addEventListener('click', () => {
            if (audio.paused) {
                if (currentIndex === -1 && queue.length > 0) {
                    currentIndex = 0;
                    playCurrentTrack(true);
                } else if (audio.src) {
                    audio.play().catch(() => {});
                }
            } else {
                audio.pause();
            }
        });
    }

    if (fsControls.previous) {
        fsControls.previous.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex -= 1;
                playCurrentTrack(true);
            }
        });
    }

    if (fsControls.next) {
        fsControls.next.addEventListener('click', () => {
            if (currentIndex < queue.length - 1) {
                currentIndex += 1;
                playCurrentTrack(true);
            }
        });
    }

    window.openFullScreenPlayer = function() {
        if (!fsModal) return;
        fsModal.classList.remove('translate-y-full');
        fsModal.classList.add('translate-y-0');
    };

    window.closeFullScreenPlayer = function() {
        if (!fsModal) return;
        fsModal.classList.remove('translate-y-0');
        fsModal.classList.add('translate-y-full');
    };

    if (fsClose) {
        fsClose.addEventListener('click', window.closeFullScreenPlayer);
    }

    document.querySelectorAll('[data-open-fullscreen-player]').forEach(el => {
        el.addEventListener('click', (e) => {
            e.stopPropagation();
            window.openFullScreenPlayer();
        });
    });

    // Tapping the bottom player bar outside controls opens full-screen player
    player.addEventListener('click', (e) => {
        if (e.target.closest('button, input, a')) return;
        window.openFullScreenPlayer();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && fsModal && !fsModal.classList.contains('translate-y-full')) {
            window.closeFullScreenPlayer();
        }
    });

    // Initialize global queue from the page so next/prev works immediately
    queue = readQueue(document);
    if (queue.length > 0) {
        currentIndex = 0;
        updateNavigation();
    }
})();
