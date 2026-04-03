// ─── Music Note Particles ─────────────────────────────────
const noteWrap = document.getElementById('notes-wrap');
const noteChars = ['♪', '♫', '♩', '♬', '𝅘𝅥𝅮'];

function spawnNote() {
    const note = document.createElement('span');
    note.classList.add('music-note');
    note.textContent = noteChars[Math.floor(Math.random() * noteChars.length)];
    note.style.left = `${Math.random() * 100}vw`;
    const dur = 7 + Math.random() * 10;
    note.style.animationDuration = `${dur}s`;
    note.style.fontSize = `${0.8 + Math.random() * 0.8}rem`;
    note.style.opacity = 0;
    noteWrap.appendChild(note);
    note.addEventListener('animationend', () => note.remove());
}
setInterval(spawnNote, 1400);

// ─── Drag & Drop ──────────────────────────────────────────
const dragOverlay = document.getElementById('drag-overlay');
let dragCounter = 0;

document.addEventListener('dragenter', e => {
    e.preventDefault();
    dragCounter++;
    dragOverlay.classList.remove('hidden');
});

document.addEventListener('dragleave', e => {
    dragCounter--;
    if (dragCounter === 0) dragOverlay.classList.add('hidden');
});

document.addEventListener('dragover', e => { e.preventDefault(); });

document.addEventListener('drop', e => {
    e.preventDefault();
    dragCounter = 0;
    dragOverlay.classList.add('hidden');
    const text = e.dataTransfer.getData('text');
    if (text) {
        document.getElementById('spotify-url').value = text;
        switchTab('download');
        showToast('🎵 Link dropped in!');
    }
});

// ─── Ctrl+V Global Shortcut ───────────────────────────────
document.addEventListener('keydown', e => {
    if (e.ctrlKey && e.key === 'v') {
        const active = document.activeElement;
        if (active && active.tagName === 'INPUT') return;
        document.getElementById('spotify-url').focus();
    }
});

// ─── Download History (localStorage) ─────────────────────
function getHistory()  { return JSON.parse(localStorage.getItem('sk_history') || '[]'); }
function saveHistory(h){ localStorage.setItem('sk_history', JSON.stringify(h)); }

function addHistoryEntry(path, format) {
    let h = getHistory();
    h.unshift({ path, format, time: new Date().toISOString() });
    if (h.length > 10) h = h.slice(0, 10);
    saveHistory(h);
    renderHistory();
}

function renderHistory() {
    const list   = document.getElementById('history-list');
    const empty  = document.getElementById('history-empty');
    const h      = getHistory();

    list.innerHTML = '';

    if (h.length === 0) {
        empty.classList.remove('hidden');
        return;
    }
    empty.classList.add('hidden');

    h.forEach(entry => {
        const item = document.createElement('div');
        item.className = 'history-item';
        const relTime = timeAgo(new Date(entry.time));
        item.innerHTML = `
            <span class="history-badge">${entry.format || 'MP3'}</span>
            <div class="history-info">
                <div class="history-path">${entry.path}</div>
                <div class="history-time">${relTime}</div>
            </div>
        `;
        list.appendChild(item);
    });
}

function timeAgo(date) {
    const diff = Math.floor((Date.now() - date.getTime()) / 1000);
    if (diff < 60)   return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

document.getElementById('clear-history-btn').addEventListener('click', () => {
    localStorage.removeItem('sk_history');
    renderHistory();
    showToast('History cleared');
});

// ─── Stats Counter ────────────────────────────────────────
function getStats()  { return parseInt(localStorage.getItem('sk_stats_total') || '0'); }
function bumpStats() {
    const n = getStats() + 1;
    localStorage.setItem('sk_stats_total', n);
    document.getElementById('stat-total').textContent = n;
}

function loadStats() {
    document.getElementById('stat-total').textContent = getStats();
}

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

    // Init on page load
    loadStats();
    renderHistory();

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
                    // Record in history and bump stats
                    addHistoryEntry(data.download_path, document.getElementById('audio-format').value.toUpperCase());
                    bumpStats();

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
