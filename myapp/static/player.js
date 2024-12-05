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

        if (!this.audio || !this.playlist) {
            console.error('Required player elements not found');
            return;
        }

        this.playlistItems = Array.from(this.playlist.getElementsByTagName('li'));
        this.currentIndex = 0;
        // Add a flag to track submission state
        this.isSubmitting = false;

        // Bind event listeners only once
        // if (!this.eventListenersSet) {
            this.setupEventListeners();
            // this.eventListenersSet = true;
        // }
        this.updateNavigationButtons();
    }

    updatePlaylistItems() {
        this.playlistItems = Array.from(this.playlist.getElementsByTagName('li'));
        this.currentIndex = 0; // Reset to first track
        this.updateNavigationButtons();
    }

    async loadTrackFromListItem(listItem, newIndex) {
        const url = listItem.dataset.url;
        const cover = listItem.querySelector('.queue-image').src;
        const title = listItem.querySelector('.queue-title').textContent;
        const artist = listItem.querySelector('.queue-artist').textContent;
    
        // Update UI
        document.querySelector('.queue-item.active')?.classList.remove('active');
        listItem.classList.add('active');
        this.currentIndex = newIndex;
    
        try {
            this.audio.src = url;
            this.coverArt.src = cover;
            this.titleElement.textContent = title;
            this.artistElement.textContent = artist;
    
            this.audio.play();
            this.updateNavigationButtons();
        } catch (error) {
            console.error('Error loading track:', error);
        }
    }

    setupEventListeners() {

        this.audio.addEventListener('ended', () => this.playNext());
        // Playlist clicks
        this.playlist.addEventListener('click', (e) => {
            const listItem = e.target.closest('.queue-item');
            if (listItem) {
                const newIndex = this.playlistItems.indexOf(listItem);
                this.loadTrackFromListItem(listItem, newIndex);
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
        // Single form submit handler
        const form = document.getElementById('playlist-form');
        if (form) {
            const oldForm = form.cloneNode(true);
            form.parentNode.replaceChild(oldForm, form);

            oldForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                if (this.isSubmitting) return false;
                
                this.isSubmitting = true;
                await this.reorganizePlaylist(e);
                
                setTimeout(() => {
                    this.isSubmitting = false;
                }, 1000);
            });
        }
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
            
            // this.audio.play();
            this.updateNavigationButtons();
        } catch (error) {
            console.error('Error loading track:', error);
        }
    }

    updateNavigationButtons() {
        this.prevBtn.disabled = this.currentIndex <= 0;
        this.nextBtn.disabled = this.currentIndex >= this.playlistItems.length - 1;
    }

    playNext() {
        if (this.currentIndex < this.playlistItems.length - 1) {
            const nextTrack = this.playlistItems[this.currentIndex + 1];
            this.loadTrackFromListItem(nextTrack, this.currentIndex + 1);
        }
    }
    
    playPrevious() {
        if (this.currentIndex > 0) {
            const prevTrack = this.playlistItems[this.currentIndex - 1];
            this.loadTrackFromListItem(prevTrack, this.currentIndex - 1);
        }
    }

    async reorganizePlaylist(e) {
        e.preventDefault();
        const instruction = e.target.instruction.value;
        const playlistId = currentPlaylistData.id; // Get the current playlist ID
    
        try {
            const response = await fetch('/reorganize-playlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ instruction, playlist_id: playlistId })
            });
    
            const data = await response.json();
            // Check HTTP status first
            if (!response.ok) {
                throw new Error(data.message || 'Server error occurred');
            }
    
            // Only update UI if we have valid playlist data
            if (data.playlist && Array.isArray(data.playlist)) {
                this.updatePlaylistUI(data.playlist);
            } else {
                throw new Error('Invalid playlist data received');
            }
        } catch (error) {
            console.error('Error reorganizing playlist:', error);
            alert('Failed to reorganize playlist');
        }
    }

    updatePlaylistUI(newPlaylist) {
        this.playlist.innerHTML = newPlaylist.map((song, index) => `
            <li class="queue-item ${index === this.currentIndex ? 'active' : ''}" data-song-id="${song.id}" data-url="${song.url}">
                <img class="queue-image" src="${song.cover}" alt="Song Cover">
                <div class="queue-details">
                    <p class="queue-title">${song.title}</p>
                    <p class="queue-artist">${song.artist}</p>
                </div>
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