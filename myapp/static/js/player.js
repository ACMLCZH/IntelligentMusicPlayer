// static/js/player.js
class MusicPlayer {
    constructor() {
        // Elements
        this.audio = document.getElementById('audio-player');
        this.coverArt = document.getElementById('cover-art');
        this.titleElement = document.getElementById('track-title');
        this.artistElement = document.getElementById('track-artist');
        this.playlist = document.getElementById('playlist-container');
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');

        // State
        this.playlistItems = Array.from(this.playlist.getElementsByTagName('li'));
        this.currentIndex = parseInt(this.playlist.dataset.currentIndex);
        
        this.setupEventListeners();
        this.updateNavigationButtons();
    }

    setupEventListeners() {
        // Playlist clicks
        this.playlist.addEventListener('click', (e) => {
            const button = e.target.closest('.song-select');
            if (button) {
                const listItem = button.closest('li');
                const newIndex = this.playlistItems.indexOf(listItem);
                this.loadTrack(button, newIndex);
            }
        });

        // Navigation
        this.prevBtn.addEventListener('click', () => this.playPrevious());
        this.nextBtn.addEventListener('click', () => this.playNext());

        // Error handling
        this.audio.addEventListener('error', (e) => {
            console.error('Audio error:', e);
            const source = this.audio.querySelector('source');
            if (source.src !== source.dataset.serverUrl) {
                source.src = source.dataset.serverUrl;
                this.audio.load();
            }
        });

        // Playlist reorganization
        document.getElementById('playlist-form')?.addEventListener('submit', 
            (e) => this.reorganizePlaylist(e));
    }

    async loadTrack(button, newIndex) {
        const listItem = button.closest('li');
        const url = button.dataset.url;
        const cover = button.dataset.cover;

        // Update UI
        document.querySelector('.active')?.classList.remove('active');
        listItem.classList.add('active');
        this.currentIndex = newIndex;

        try {
            // Try cache first
            const audioResponse = await caches.match(url);
            const coverResponse = await caches.match(cover);
            
            this.audio.src = audioResponse ? await audioResponse.url : url;
            this.coverArt.src = coverResponse ? await coverResponse.url : cover;
            this.titleElement.textContent = button.dataset.title;
            this.artistElement.textContent = button.dataset.artist;
            
            this.audio.play();
            this.updateNavigationButtons();
        } catch (error) {
            console.error('Error loading track:', error);
        }
    }

    updateNavigationButtons() {
        this.prevBtn.disabled = this.currentIndex === 0;
        this.nextBtn.disabled = this.currentIndex === this.playlistItems.length - 1;
    }

    playNext() {
        if (this.currentIndex < this.playlistItems.length - 1) {
            const nextTrack = this.playlistItems[this.currentIndex + 1];
            const button = nextTrack.querySelector('.song-select');
            this.loadTrack(button, this.currentIndex + 1);
        }
    }

    playPrevious() {
        if (this.currentIndex > 0) {
            const prevTrack = this.playlistItems[this.currentIndex - 1];
            const button = prevTrack.querySelector('.song-select');
            this.loadTrack(button, this.currentIndex - 1);
        }
    }

    async reorganizePlaylist(e) {
        e.preventDefault();
        const instruction = e.target.instruction.value;

        try {
            const response = await fetch('/reorganize-playlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ instruction })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.updatePlaylistUI(data.playlist);
            } else {
                alert(data.message);
            }
        } catch (error) {
            console.error('Error reorganizing playlist:', error);
            alert('Failed to reorganize playlist');
        }
    }

    updatePlaylistUI(newPlaylist) {
        this.playlist.innerHTML = newPlaylist.map((song, index) => `
            <li data-song-id="${song.id}" ${index === this.currentIndex ? 'class="active"' : ''}>
                <button class="song-select" 
                    data-url="${song.url}"
                    data-cover="${song.cover}"
                    data-title="${song.title}"
                    data-artist="${song.artist}">
                    <i class="fas fa-music"></i> ${song.title} - ${song.artist}
                </button>
            </li>
        `).join('');
        this.playlistItems = Array.from(this.playlist.getElementsByTagName('li'));
        this.updateNavigationButtons();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MusicPlayer();
});