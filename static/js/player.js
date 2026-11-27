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

    let queue = [];
    let currentIndex = -1;
    let lastAudibleVolume = 0.8;

    function formatTime(value) {
        if (!Number.isFinite(value) || value < 0) return '0:00';
        const seconds = Math.floor(value);
        return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
    }

    function setStatus(message, state) {
        controls.status.textContent = message;
        player.dataset.playerState = state;
    }

    function updateNavigation() {
        const active = currentIndex >= 0 && queue.length > 0;
        controls.previous.disabled = !active || currentIndex <= 0;
        controls.next.disabled = !active || currentIndex >= queue.length - 1;
        controls.toggle.disabled = !active;
        controls.volume.disabled = !active;
        controls.mute.disabled = !active;
    }

    function readQueue(container) {
        return Array.from(container.querySelectorAll('[data-player-track]'))
            .map((button) => ({
                src: button.dataset.audioUrl,
                title: button.dataset.trackTitle || 'Untitled track',
                artist: button.dataset.trackArtist || 'Unknown artist',
                album: button.dataset.trackAlbum || '',
                cover: button.dataset.trackCover || '',
            }))
            .filter((track) => track.src);
    }

    function updateArtwork(url) {
        controls.artwork.onerror = () => {
            controls.artwork.hidden = true;
            controls.artworkFallback.hidden = false;
        };
        if (url) {
            controls.artwork.src = url;
            controls.artwork.hidden = false;
            controls.artworkFallback.hidden = true;
        } else {
            controls.artwork.removeAttribute('src');
            controls.artwork.hidden = true;
            controls.artworkFallback.hidden = false;
        }
    }

    function playCurrentTrack(shouldPlay) {
        const track = queue[currentIndex];
        if (!track) return;

        audio.pause();
        audio.src = track.src;
        audio.load();
        controls.title.textContent = track.title;
        controls.artist.textContent = track.artist || track.album || 'Unknown artist';
        controls.currentTime.textContent = '0:00';
        controls.duration.textContent = '0:00';
        controls.seek.value = '0';
        controls.seek.disabled = true;
        controls.toggle.textContent = '▶';
        controls.toggle.setAttribute('aria-label', 'Play');
        updateArtwork(track.cover);
        updateNavigation();
        setStatus(`Loading ${track.title}…`, 'loading');

        if (shouldPlay) {
            audio.play().catch((error) => {
                const message = error && error.name === 'NotAllowedError'
                    ? 'Playback was blocked by the browser. Press Play to try again.'
                    : 'This audio file could not be played. Try another track.';
                setStatus(message, 'error');
            });
        }
    }

    function startFrom(container, clickedButton, playAll) {
        queue = readQueue(container);
        if (!queue.length) {
            setStatus('There are no available audio files in this queue.', 'unavailable');
            currentIndex = -1;
            updateNavigation();
            return;
        }
        currentIndex = playAll
            ? 0
            : queue.findIndex((track) => track.src === clickedButton.dataset.audioUrl);
        if (currentIndex < 0) {
            setStatus('This audio file is unavailable. Choose another track.', 'unavailable');
            updateNavigation();
            return;
        }
        playCurrentTrack(true);
    }

    document.addEventListener('click', (event) => {
        const playAllButton = event.target.closest('[data-player-play-all]');
        if (playAllButton) {
            const container = playAllButton.closest('[data-player-queue]');
            if (container) startFrom(container, null, true);
            return;
        }

        const trackButton = event.target.closest('[data-player-track]');
        if (trackButton) {
            const container = trackButton.closest('[data-player-queue]');
            if (container) startFrom(container, trackButton, false);
        }
    });

    controls.toggle.addEventListener('click', () => {
        if (audio.paused) {
            audio.play().catch(() => setStatus('This audio file could not be played. Try another track.', 'error'));
        } else {
            audio.pause();
        }
    });

    controls.previous.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex -= 1;
            playCurrentTrack(true);
        }
    });

    controls.next.addEventListener('click', () => {
        if (currentIndex >= 0 && currentIndex < queue.length - 1) {
            currentIndex += 1;
            playCurrentTrack(true);
        }
    });

    controls.seek.addEventListener('input', () => {
        if (Number.isFinite(audio.duration) && audio.duration > 0) {
            audio.currentTime = (Number(controls.seek.value) / Number(controls.seek.max)) * audio.duration;
        }
    });

    controls.volume.addEventListener('input', () => {
        audio.volume = Number(controls.volume.value);
        audio.muted = audio.volume === 0;
        if (audio.volume > 0) lastAudibleVolume = audio.volume;
        controls.mute.textContent = audio.muted ? '🔇' : '🔊';
        controls.mute.setAttribute('aria-label', audio.muted ? 'Unmute' : 'Mute');
    });

    controls.mute.addEventListener('click', () => {
        if (audio.muted || audio.volume === 0) {
            audio.muted = false;
            audio.volume = lastAudibleVolume || 0.8;
            controls.volume.value = String(audio.volume);
        } else {
            lastAudibleVolume = audio.volume;
            audio.muted = true;
        }
        controls.mute.textContent = audio.muted ? '🔇' : '🔊';
        controls.mute.setAttribute('aria-label', audio.muted ? 'Unmute' : 'Mute');
    });

    audio.addEventListener('loadstart', () => setStatus('Loading audio…', 'loading'));
    audio.addEventListener('canplay', () => {
        controls.seek.disabled = false;
        controls.seek.max = '1000';
        if (audio.paused) setStatus('Ready to play', 'paused');
    });
    audio.addEventListener('loadedmetadata', () => {
        controls.duration.textContent = formatTime(audio.duration);
    });
    audio.addEventListener('timeupdate', () => {
        controls.currentTime.textContent = formatTime(audio.currentTime);
        controls.duration.textContent = formatTime(audio.duration);
        if (Number.isFinite(audio.duration) && audio.duration > 0) {
            controls.seek.value = String(Math.round((audio.currentTime / audio.duration) * 1000));
        }
    });
    audio.addEventListener('play', () => {
        controls.toggle.textContent = '❚❚';
        controls.toggle.setAttribute('aria-label', 'Pause');
    });
    audio.addEventListener('playing', () => setStatus(`Playing ${controls.title.textContent}`, 'playing'));
    audio.addEventListener('pause', () => {
        if (!audio.ended && audio.src) {
            controls.toggle.textContent = '▶';
            controls.toggle.setAttribute('aria-label', 'Play');
            setStatus(`Paused ${controls.title.textContent}`, 'paused');
        }
    });
    audio.addEventListener('ended', () => {
        if (currentIndex < queue.length - 1) {
            currentIndex += 1;
            playCurrentTrack(true);
        } else {
            controls.toggle.textContent = '▶';
            controls.toggle.setAttribute('aria-label', 'Play');
            setStatus('Playlist queue finished.', 'ended');
        }
    });
    audio.addEventListener('error', () => {
        controls.seek.disabled = true;
        setStatus('This audio file is unavailable or could not be loaded. Try another track.', 'error');
    });

    audio.volume = Number(controls.volume.value);
})();
