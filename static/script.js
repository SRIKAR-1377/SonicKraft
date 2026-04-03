// ─── Tab Switching ─────────────────────────────────────────
function switchTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');
    document.getElementById(`panel-${tab}`).classList.add('active');
}

// ─── Toast Notification ─────────────────────────────────────
function showToast(msg = '✓ Copied!') {
    const toast = document.getElementById('toast');
    document.getElementById('toast-msg').textContent = msg;
    toast.classList.remove('hidden');
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.classList.add('hidden'), 400);
    }, 2000);
}

// ─── Helpers ────────────────────────────────────────────────
function showError(id, message) {
    const el = document.getElementById(id);
    el.textContent = message;
    el.classList.remove('hidden');
}

function clearError(id) {
    const el = document.getElementById(id);
    el.classList.add('hidden');
    el.textContent = '';
}

// ─── DOWNLOAD PANEL ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const inputUrl    = document.getElementById('spotify-url');
    const inputPath   = document.getElementById('download-path');
    const btnDownload = document.getElementById('download-btn');
    const btnText     = btnDownload.querySelector('.btn-text');
    const btnLoader   = document.getElementById('btn-loader');
    const statusPanel = document.getElementById('status-panel');
    const statusText  = document.getElementById('status-text');
    const errorMsg    = document.getElementById('error-message');
    const successDiv  = document.getElementById('success-link');
    const successPath = document.getElementById('success-path');

    // Enter key support
    inputUrl.addEventListener('keydown', e => {
        if (e.key === 'Enter') btnDownload.click();
    });

    btnDownload.addEventListener('click', async () => {
        const url           = inputUrl.value.trim();
        const download_path = inputPath.value.trim();
        const format_choice = document.getElementById('audio-format').value;

        if (!url) return showError('error-message', 'Please enter a valid Spotify URL.');
        if (!url.includes('spotify.com')) return showError('error-message', 'The URL doesn\'t look like a valid Spotify link.');

        // Reset
        clearError('error-message');
        successDiv.classList.add('hidden');

        // Loading state
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        btnDownload.disabled = true;
        statusPanel.classList.remove('hidden');
        statusText.textContent = 'Establishing connection...';

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, download_path, format_choice })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Failed to start download.');

            pollStatus(data.session_id);

        } catch (error) {
            showError('error-message', error.message);
            restoreDownloadUI();
        }
    });

    function pollStatus(sessionId) {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${sessionId}`);
                const data     = await response.json();

                if (!response.ok) throw new Error(data.error || 'Failed to get status.');

                if (data.status === 'downloading' || data.status === 'starting') {
                    // Fade text update
                    statusText.style.opacity = '0';
                    setTimeout(() => {
                        statusText.textContent = data.message || 'Processing...';
                        statusText.style.opacity = '1';
                    }, 150);

                } else if (data.status === 'completed') {
                    clearInterval(interval);
                    statusPanel.classList.add('hidden');
                    successPath.textContent = `Saved to: ${data.download_path}`;
                    successDiv.classList.remove('hidden');
                    restoreDownloadUI();
                    showToast('🎵 Download Complete!');

                } else if (data.status === 'error') {
                    clearInterval(interval);
                    showError('error-message', data.message || 'An unknown error occurred.');
                    restoreDownloadUI();
                }
            } catch (error) {
                clearInterval(interval);
                showError('error-message', 'Lost connection while downloading.');
                restoreDownloadUI();
            }
        }, 2500);
    }

    function restoreDownloadUI() {
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
        btnDownload.disabled = false;
        statusPanel.classList.add('hidden');
    }

    // ─── TRANSLATE PANEL ──────────────────────────────────────
    const convertInput    = document.getElementById('convert-url');
    const convertBtn      = document.getElementById('convert-btn');
    const convertBtnText  = convertBtn.querySelector('.btn-text-convert');
    const convertLoader   = document.getElementById('convert-loader');
    const convertResults  = document.getElementById('convert-results');
    const platformLinks   = document.getElementById('platform-links');

    // Enter key support
    convertInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') convertBtn.click();
    });

    convertBtn.addEventListener('click', async () => {
        const url = convertInput.value.trim();
        if (!url) return showError('convert-error', 'Please enter a URL to translate.');

        clearError('convert-error');
        convertResults.classList.add('hidden');
        convertBtnText.classList.add('hidden');
        convertLoader.classList.remove('hidden');
        convertBtn.disabled = true;

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Failed to translate link.');

            renderPlatformLinks(data.links);

        } catch (error) {
            showError('convert-error', error.message);
        } finally {
            convertBtnText.classList.remove('hidden');
            convertLoader.classList.add('hidden');
            convertBtn.disabled = false;
        }
    });

    function renderPlatformLinks(links) {
        platformLinks.innerHTML = '';

        const icons = {
            spotify:      '🟢',
            youtubeMusic: '🔴',
            youtube:      '▶️',
            appleMusic:   '🍎',
            soundcloud:   '🟠',
            tidal:        '🔵',
            deezer:       '💜',
        };

        const names = {
            spotify:      'Spotify',
            youtubeMusic: 'YouTube Music',
            youtube:      'YouTube',
            appleMusic:   'Apple Music',
            soundcloud:   'SoundCloud',
            tidal:        'Tidal',
            deezer:       'Deezer',
        };

        for (const [platform, url] of Object.entries(links)) {
            const a = document.createElement('a');
            a.href = url;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            a.className = 'platform-link';
            a.innerHTML = `
                <span>${icons[platform] || '🎵'}</span>
                <span>${names[platform] || platform}</span>
                <span class="copy-btn" title="Copy link">⎘</span>
            `;

            // Click copy icon without navigating
            a.querySelector('.copy-btn').addEventListener('click', e => {
                e.preventDefault();
                e.stopPropagation();
                navigator.clipboard.writeText(url).then(() => {
                    showToast(`✓ ${names[platform] || platform} link copied!`);
                });
            });

            platformLinks.appendChild(a);
        }

        convertResults.classList.remove('hidden');
    }
});
