let accessibleFavlists = [];
let currentPlaylistData = null;
let currentPlayQueue = null;
// Declare a global variable to hold the MusicPlayer instance
let player = null;
let currentAIData = null;

document.addEventListener('DOMContentLoaded', function() {
    // Load user playlists and set up the navigation bar
    fetchPlayLists();
    setupNavbar();

    // Initialize the music player instance
    player = new MusicPlayer();

    // Click event for playlist items
    document.getElementById('playlist-list').addEventListener('click', function(e) {
        let target = e.target.closest('li');
        if (target) {
            let playlistId = target.dataset.id;
            console.log(`Fetching details for playlist ID: ${playlistId}`);
            fetchPlayList(playlistId);

            let playlistItems = document.querySelectorAll('#playlist-list li');
            playlistItems.forEach(function(item) {
                item.classList.remove('active');
            });

            target.classList.add('active');
        }
    });

    // "Add to play queue" button event
    document.getElementById('add-to-playqueue').addEventListener('click', function() {
        const playQueue = document.getElementById('playlist-container');
        currentPlayQueue = currentPlaylistData.songs_detail.map(song => ({
            id: song.id,
            title: song.name,
            artist: song.author,
            cover: song.cover_url,
            url: song.mp3_url
        }));
    
        playQueue.innerHTML = currentPlayQueue.map((song, index) => `
            <li class="queue-item ${index === 0 ? 'active' : ''}" data-song-id="${song.id}" data-url="${song.url}">
                <img class="queue-image" src="${song.cover}" alt="Song Cover">
                <div class="queue-details">
                    <p class="queue-title">${song.title}</p>
                    <p class="queue-artist">${song.artist}</p>
                </div>
            </li>
        `).join('');
    
        if (player) {
            player.updatePlaylistItems();
            player.loadCurrentTrack();
        }
    });
    
    // Adjust the NLP input box height based on input
    document.getElementById('nlp-input').addEventListener('input', function () {
        this.style.height = 'auto'; 
        this.style.height = this.scrollHeight + 'px';
    });

    // Set placeholder examples for NLP commands
    const nlpExamples = [
        "Shuffle my queue",
        "Play Summer Rain every two songs",
        "Play Jazz music",
    ];
    
    const nlpInput = document.getElementById('nlp-input');
    
    // Set a random initial example as a placeholder
    let currentIndex = Math.floor(Math.random() * nlpExamples.length);
    nlpInput.placeholder = `You can say "${nlpExamples[currentIndex]}"`;
    
    // Cycle through the examples every 3 seconds
    setInterval(() => {
        currentIndex = (currentIndex + 1) % nlpExamples.length;
        nlpInput.placeholder = `You can say "${nlpExamples[currentIndex]}"`;
    }, 3000);

    // Event listener for the "Add Playlist" button
    document.getElementById('add-playlist-button').addEventListener('click', function() {
        toggleAddPlaylistDropdown();
    });

    // Event listener for "Create Playlist" button
    document.getElementById('create-playlist-button').addEventListener('click', function() {
        createNewPlaylist();
    });

    // Close dropdown when clicking outside of it
    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById('add-playlist-dropdown');
        const addButton = document.getElementById('add-playlist-button');
        if (!dropdown.contains(e.target) && e.target !== addButton) {
            dropdown.style.display = 'none';
        }
    });

    // AI generate button event
    document.getElementById('ai-generate-button').addEventListener('click', function() {
        if (currentAIData) {
            displayAIData();
        } else {
            generateSongsWithAI();
        }
    });

    // Right-click event on playlists to show context menu
    document.getElementById('playlist-list').addEventListener('contextmenu', function(e) {
        e.preventDefault();
        let target = e.target.closest('li');
        if (target) {
            showPlaylistContextMenu(e, target);
        }
    });

    // Right-click event on songs to show context menu
    document.getElementById('songs-list').addEventListener('contextmenu', function(e) {
        e.preventDefault();
        let target = e.target.closest('.song-item');
        if (target) {
            showSongContextMenu(e, target);
        }
    });

    // Close context menus when clicking outside
    document.addEventListener('click', function(e) {
        closeContextMenus();
    });

    // "Add to favlist" button in the player area
    document.getElementById('add-to-playlist-btn').addEventListener('click', function(e) {
        e.stopPropagation();
        const currentSong = getCurrentPlayingSong();
        if (currentSong) {
            showFavlistDropdownInPlayer(currentSong.id, this);
        } else {
        }
    });

    // Close the favlist dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const dropdown = document.querySelector('.favlist-dropdown');
        if (dropdown && !dropdown.contains(e.target)) {
            dropdown.remove();
        }
    });
    
});

/**
 * Sets up the navigation bar with event listeners for search and user menu.
 */
function setupNavbar() {
    console.log('Setting up navbar');
    // "Home" link click event to navigate to homepage
    document.getElementById('home-link').addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/index';
    });

    // Click event on search button
    document.getElementById('search-button').addEventListener('click', function() {
        let query = document.getElementById('search-input').value.trim();
        if (query) {
            performSearch(query);
        }
    });

    // Press Enter to search
    document.getElementById('search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            let query = document.getElementById('search-input').value.trim();
            if (query) {
                performSearch(query);
            }
        }
    });

    // Toggle user menu when avatar is clicked
    const userAvatar = document.getElementById('user-avatar');
    const navUser = document.querySelector('.nav-user');

    userAvatar.addEventListener('click', function() {
        navUser.classList.toggle('active');
    });

    // Close user menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navUser.contains(e.target)) {
            navUser.classList.remove('active');
        }
    });

    // Logout event
    document.getElementById('logout').addEventListener('click', function(e) {
        e.preventDefault();
        logoutUser();
    });

    // Edit profile link is deleted, no action required here
}

/**
 * Performs a search request for songs matching the given query.
 * @param {string} query - The search query.
 */
function performSearch(query) {
    console.log('Searching for:', query);

    // Hide the playlist info section during search results
    document.querySelector('.playlist-info').style.display = 'none';

    fetch(`/song/search/?search=${encodeURIComponent(query)}&limit=20`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error during search: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            console.log('Search API response data:', data);
            if (Array.isArray(data.results)) {
                displaySongs(data.results);
            } else {
                console.error('Unexpected API response:', data);
                displayNoResults();
            }
        })
        .catch(error => {
            console.error('Error during search:', error);
        });
}

/**
 * Formats song duration from seconds to MM:SS.
 * @param {number} seconds - The song duration in seconds.
 * @returns {string} The formatted duration as MM:SS.
 */
function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

/**
 * Displays a list of songs (either from a playlist or search results).
 * @param {Array} songs - An array of song objects.
 */
function displaySongs(songs) {
    console.log(songs);
    const songsList = document.getElementById('songs-list');
    songsList.innerHTML = ''; // Clear previous content

    songs.forEach((song, index) => {
        const songItem = document.createElement('div');
        songItem.classList.add('song-item');
        songItem.dataset.songId = song.id;

        songItem.innerHTML = `
            <div class="song-rank">${index + 1}</div>
            <img class="song-image" src="${song.cover_url}" alt="Song Cover">
            <div class="song-details">
                <p class="song-title">${song.name}</p>
                <p class="song-artist">${song.author}</p>
            </div>
            <div class="song-album">${song.album}</div>
            <div class="song-duration">${formatDuration(song.duration)}</div>
            <div class="song-actions">
                <img class="add-to-favlist-button" src="/static/add.webp" alt="Add to Favlist">
            </div>
        `;

        songItem.style.userSelect = 'none';

        // Double-click to play a single song
        songItem.addEventListener('dblclick', () => {
            currentPlayQueue = [{
                id: song.id,
                title: song.name,
                artist: song.author,
                cover: song.cover_url,
                url: song.mp3_url
            }];

            // Update the play queue UI
            const playQueue = document.getElementById('playlist-container');
            playQueue.innerHTML = `
                <li class="queue-item active" data-song-id="${song.id}" data-url="${song.mp3_url}">
                    <img class="queue-image" src="${song.cover_url}" alt="Song Cover">
                    <div class="queue-details">
                        <p class="queue-title">${song.name}</p>
                        <p class="queue-artist">${song.author}</p>
                    </div>
                </li>
            `;
            
            if (player) {
                player.updatePlaylistItems();
                player.loadCurrentTrack();
            }
        });

        // "Add to favlist" button event
        const addButton = songItem.querySelector('.add-to-favlist-button');
        addButton.addEventListener('click', (e) => {
            e.stopPropagation(); 
            showFavlistDropdown(song.id, addButton);
        });

        songsList.appendChild(songItem);
    });
    
    const playlistCover = document.getElementById('playlist-cover');
    if (songs.length > 0) {
        const randomIndex = Math.floor(Math.random() * songs.length);
        const randomSong = songs[randomIndex];
        playlistCover.src = randomSong.cover_url;
    } else {
        playlistCover.src = '/static/default-cover.jpg';
    }
}

/**
 * Fetches the user's playlists from the server.
 * @param {number|null} selectedPlaylistId - Optional playlist ID to be selected after fetch.
 */
function fetchPlayLists(selectedPlaylistId = null) {
    console.log(`selectedPlaylistId: ${selectedPlaylistId}`);
    fetch('/userfav/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            accessibleFavlists = data.favlists_detail; 
            displayPlayLists(data.favlists_detail, selectedPlaylistId);
        })
        .catch(error => {
            console.error('Error fetching playlists:', error);
        });
}

/**
 * Displays the fetched playlists in the UI.
 * @param {Array} playlists - Array of playlist objects.
 * @param {number|null} selectedPlaylistId - Playlist ID to select automatically.
 */
function displayPlayLists(playlists, selectedPlaylistId = null) {
    let playlistList = document.getElementById('playlist-list');
    playlistList.innerHTML = ''; // Clear existing playlists

    playlists.forEach(function(playlist) {
        let li = document.createElement('li');
        li.textContent = playlist.name; 
        li.dataset.id = playlist.id;
        playlistList.appendChild(li);

        playlistList.style.userSelect = 'none';
    });

    // Automatically select and load a specified playlist, or the first one if none specified
    if (selectedPlaylistId && playlistList) {
        const selectedItem = playlistList.querySelector(`li[data-id="${selectedPlaylistId.toString()}"]`);
        console.log(`Selected playlist ID: ${selectedPlaylistId}`);
        if (selectedItem) {
            selectedItem.click();
        } else {
            console.log('Selected item not found in the playlist.');
        }
    } else {
        playlistList.firstElementChild.click();
    }
}

/**
 * Fetches details (songs) of the specified playlist by ID.
 * @param {number} playlistId - The ID of the playlist to fetch.
 */
function fetchPlayList(playlistId) {
    fetch(`/favlist/${playlistId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            currentPlaylistData = data; 
            window.currentPlaylistData = currentPlaylistData;
            displayPlayList(data);
        })
        .catch(error => {
            console.error('Error fetching playlists:', error);
        });
}

/**
 * Displays a playlist (title, songs, AI generate button).
 * @param {Object} playListData - Playlist data object.
 */
function displayPlayList(playListData) {
    document.querySelector('.playlist-info').style.display = 'flex';
    document.getElementById('current-playlist-title').textContent = playListData.name;
    document.getElementById('ai-generate-button').style.display = 'flex';
    document.getElementById('add-to-playqueue').style.display = 'flex';
    console.log(playListData);
    displaySongs(playListData.songs_detail);
}

/**
 * Toggles the collection (favorite) status of a song.
 * @param {number} songId - Song ID.
 * @param {HTMLElement} buttonElement - The button element clicked.
 */
function toggleCollection(songId, buttonElement) {
    console.log("Toggled favorite status for song ID:", songId);

    // Example: Update the button text to show toggled state
    let isFavorited = buttonElement.textContent === 'F';
    buttonElement.textContent = isFavorited ? 'U' : 'F';
}

/**
 * Updates the play queue based on a natural language command.
 * (This is a placeholder simulation.)
 * @param {string} command - Natural language command.
 */
function updatePlayQueue(command) {
    console.log("Updating play queue with command:", command);
    let newPlayQueue = [
        {"id": 8, "title": "New Song 1"},
        {"id": 9, "title": "New Song 2"}
    ];
    displayPlayQueue(newPlayQueue);
}

/**
 * Displays the play queue items.
 * @param {Array} queue - Array of song objects in the queue.
 */
function displayPlayQueue(queue) {
    let playQueueList = document.getElementById('play-queue-list');
    playQueueList.innerHTML = ''; // Clear previous queue

    queue.forEach(function(song, index) {
        let li = document.createElement('li');
        li.textContent = (index === 0 ? "Now Playing: " : "") + song.title;
        playQueueList.appendChild(li);
    });
    
    if (player) {
        player.updatePlaylistItems();
    }
}

/**
 * Shows a dropdown of user's favorite playlists (favlists) to add a song into.
 * @param {number} songId - ID of the song to add.
 * @param {HTMLElement} addButtonElement - The clicked button element.
 */
function showFavlistDropdown(songId, addButtonElement) {
    // Remove any existing dropdowns
    const existingDropdown = document.querySelector('.favlist-dropdown');
    if (existingDropdown) {
        existingDropdown.parentNode.removeChild(existingDropdown);
    }

    const dropdown = document.createElement('div');
    dropdown.classList.add('favlist-dropdown');

    const rect = addButtonElement.getBoundingClientRect();
    dropdown.style.position = 'absolute';
    dropdown.style.left = `${rect.left + window.scrollX}px`;
    dropdown.style.top = `${rect.bottom + window.scrollY}px`;
    dropdown.style.zIndex = 9999;
    dropdown.style.backgroundColor = 'white';
    dropdown.style.border = '1px solid #ccc';
    dropdown.style.borderRadius = '4px';
    dropdown.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';
    dropdown.style.maxHeight = '200px';
    dropdown.style.overflowY = 'auto';
    dropdown.style.width = '150px';

    accessibleFavlists.forEach(favlist => {
        const item = document.createElement('div');
        item.textContent = favlist.name;
        item.style.padding = '10px';
        item.style.cursor = 'pointer';
        item.addEventListener('click', () => {
            addSongToFavlist(favlist.id, songId);
            if (dropdown.parentNode) {
                dropdown.parentNode.removeChild(dropdown);
            }
        });
        dropdown.appendChild(item);
    });

    document.body.appendChild(dropdown);

    document.addEventListener('click', function onClickOutside(event) {
        if (!dropdown.contains(event.target) && event.target !== addButtonElement) {
            if (dropdown.parentNode) {
                dropdown.parentNode.removeChild(dropdown);
            }
            document.removeEventListener('click', onClickOutside);
        }
    });
}

/**
 * Adds a song to the specified favlist (playlist).
 * @param {number} favlistId - The ID of the favlist.
 * @param {number|null} songId - The ID of the song to add.
 */
function addSongToFavlist(favlistId, songId) {
    if (songId === null) {
        alert('Cannot add current song to favlist.');
        return;
    }

    fetch(`/favlist/${favlistId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(favlistData => {
            let existingSongs = favlistData.songs; 
            if (!existingSongs.includes(songId)) {
                existingSongs.push(songId);
            } else {
                console.log('Song already in the favlist');
                return;
            }

            fetch(`/favlist/${favlistId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken() 
                },
                body: JSON.stringify({ songs: existingSongs })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error updating favlist: ' + response.statusText);
                }
                return response.json();
            })
            .then(updatedFavlist => {
                console.log('Song added to favlist:', updatedFavlist);
            })
            .catch(error => {
                console.error('Error adding song to favlist:', error);
            });
        })
        .catch(error => {
            console.error('Error fetching favlist data:', error);
        });
}

/**
 * Toggles the "Add Playlist" dropdown visibility.
 */
function toggleAddPlaylistDropdown() {
    const dropdown = document.getElementById('add-playlist-dropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
}

/**
 * Creates a new playlist from the user input.
 */
function createNewPlaylist() {
    const playlistNameInput = document.getElementById('new-playlist-name');
    const playlistName = playlistNameInput.value.trim();
    if (playlistName === '') {
        alert('Please enter a playlist name.');
        return;
    }

    postNewFavlist(playlistName);
}

/**
 * Sends a POST request to create a new favlist with the given name.
 * @param {string} playlistName - The name of the new playlist.
 */
function postNewFavlist(playlistName) {
    fetch('/favlist/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken() 
        },
        body: JSON.stringify({
            name: playlistName,
            songs: [] 
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error creating playlist: ' + response.statusText);
        }
        return response.json();
    })
    .then(newFavlist => {
        console.log('New favlist created:', newFavlist);
        updateUserFavlists(newFavlist.id);
        document.getElementById('new-playlist-name').value = '';
        document.getElementById('add-playlist-dropdown').style.display = 'none';
    })
    .catch(error => {
        console.error('Error creating new favlist:', error);
        alert('Error creating playlist. Please try again.');
    });
}

/**
 * Updates the user's favlists after creating a new one.
 * @param {number} newFavlistId - The ID of the newly created favlist.
 */
function updateUserFavlists(newFavlistId) {
    fetch('/userfav/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error fetching user favlists: ' + response.statusText);
            }
            return response.json();
        })
        .then(userFavData => {
            let existingFavlists = userFavData.favlists;
            if (!existingFavlists.includes(newFavlistId)) {
                existingFavlists.push(newFavlistId);
            }

            fetch('/userfav/', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ favlists: existingFavlists })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error updating user favlists: ' + response.statusText);
                }
                return response.json();
            })
            .then(updatedUserFav => {
                console.log('User favlists updated:', updatedUserFav);
                fetchPlayLists(newFavlistId);
            })
            .catch(error => {
                console.error('Error updating user favlists:', error);
                alert('Error updating your playlists. Please try again.');
            });
        })
        .catch(error => {
            console.error('Error fetching user favlists:', error);
            alert('Error fetching your playlists. Please try again.');
        });
}

/**
 * Retrieves the CSRF token from cookies.
 * @returns {string|null} The CSRF token.
 */
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i=0; i<cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Logs out the user by sending a logout request.
 */
function logoutUser() {
    fetch('/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/login/';
        } else {
            throw new Error('Logout failed.');
        }
    })
    .catch(error => {
        console.error('Error during logout:', error);
        alert('An error occurred during logout. Please try again.');
    });
}

/**
 * Displays AI-generated songs in the playlist view.
 */
function displayAIData() {
    const button = document.getElementById('ai-generate-button');
    button.textContent = 'AI';

    document.querySelector('.playlist-info').style.display = 'flex';
    document.getElementById('current-playlist-title').textContent = 'AI Generation';
    document.getElementById('ai-generate-button').style.display = 'none';
    document.getElementById('add-to-playqueue').style.display = 'none';
    displaySongs(currentAIData);
    currentAIData = null;
}

/**
 * Initiates the AI song generation process for the currently selected playlist.
 */
function generateSongsWithAI() {
    if (!currentPlaylistData || !currentPlaylistData.id) {
        alert('No playlist selected.');
        return;
    }

    const playlistId = currentPlaylistData.id;

    const controller = new AbortController();
    const signal = controller.signal;

    const button = document.getElementById('ai-generate-button');
    button.disabled = true;

    fetch(`/generate-songs/${playlistId}/`, { signal })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error generating songs: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            button.disabled = false;
            if (Array.isArray(data)) {
                button.textContent = 'OK';
                currentAIData = data;
            } else {
                console.error('Unexpected API response:', data);
                alert('Error: Unexpected response from the server.');
            }
        })
        .catch(error => {
            if (error.name === 'AbortError') {
                console.log('Request canceled');
            } else {
                console.error('Error generating songs:', error);
                alert('An error occurred while generating songs.');
            }
            button.disabled = false;
        });
}

/**
 * Shows a loading spinner overlay with a cancel button.
 * @param {AbortController} controller - The abort controller to cancel the request.
 */
function showLoadingSpinner(controller) {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    overlay.style.zIndex = 10000;
    overlay.style.display = 'flex';
    overlay.style.flexDirection = 'column';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';

    const spinner = document.createElement('div');
    spinner.classList.add('spinner');

    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.style.marginTop = '20px';
    cancelButton.style.padding = '10px 20px';
    cancelButton.style.fontSize = '16px';
    cancelButton.style.cursor = 'pointer';
    cancelButton.addEventListener('click', function() {
        controller.abort(); 
        hideLoadingSpinner();
    });

    overlay.appendChild(spinner);
    overlay.appendChild(cancelButton);

    document.body.appendChild(overlay);
}

/**
 * Hides the loading spinner overlay if present.
 */
function hideLoadingSpinner() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        document.body.removeChild(overlay);
    }
}

/**
 * Displays a context menu for a playlist (e.g., delete option).
 * @param {MouseEvent} event - The contextmenu event.
 * @param {HTMLElement} playlistItem - The clicked playlist element.
 */
function showPlaylistContextMenu(event, playlistItem) {
    closeContextMenus();

    const menu = document.createElement('div');
    menu.classList.add('context-menu');
    menu.style.top = `${event.pageY}px`;
    menu.style.left = `${event.pageX}px`;

    const deleteOption = document.createElement('div');
    deleteOption.textContent = 'Delete Playlist';
    deleteOption.addEventListener('click', function() {
        const playlistId = playlistItem.dataset.id;
        deletePlaylist(playlistId);
        menu.remove();
    });

    menu.appendChild(deleteOption);
    document.body.appendChild(menu);
}

/**
 * Displays a context menu for a song (e.g., remove from playlist).
 * @param {MouseEvent} event - The contextmenu event.
 * @param {HTMLElement} songItem - The clicked song element.
 */
function showSongContextMenu(event, songItem) {
    closeContextMenus();

    const menu = document.createElement('div');
    menu.classList.add('context-menu');
    menu.style.top = `${event.pageY}px`;
    menu.style.left = `${event.pageX}px`;

    const removeOption = document.createElement('div');
    removeOption.textContent = 'Remove Song from Playlist';
    removeOption.addEventListener('click', function() {
        const songId = parseInt(songItem.dataset.songId);
        const playlistId = currentPlaylistData.id;
        removeSongFromPlaylist(playlistId, songId);
        menu.remove();
    });

    menu.appendChild(removeOption);
    document.body.appendChild(menu);
}

/**
 * Closes all open context menus.
 */
function closeContextMenus() {
    const existingMenus = document.querySelectorAll('.context-menu');
    existingMenus.forEach(menu => menu.remove());
}

/**
 * Deletes a playlist by its ID.
 * @param {number} playlistId - The ID of the playlist to delete.
 */
function deletePlaylist(playlistId) {
    if (!confirm('Are you sure you want to delete this playlist?')) {
        return;
    }

    fetch(`/favlist/${playlistId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
    .then(response => {
        if (response.ok) {
            const playlistItem = document.querySelector(`#playlist-list li[data-id='${playlistId}']`);
            if (playlistItem) {
                playlistItem.remove();
            }
            if (currentPlaylistData && currentPlaylistData.id == playlistId) {
                document.getElementById('songs-list').innerHTML = '';
                document.getElementById('current-playlist-title').textContent = 'Playlist Title';
            }
            alert('Playlist deleted successfully.');
        } else {
            throw new Error('Failed to delete playlist.');
        }
    })
    .catch(error => {
        console.error('Error deleting playlist:', error);
        alert('An error occurred while deleting the playlist.');
    });
}

/**
 * Removes a song from a playlist.
 * @param {number} playlistId - The ID of the playlist.
 * @param {number} songId - The ID of the song to remove.
 */
function removeSongFromPlaylist(playlistId, songId) {
    if (!confirm('Are you sure you want to remove this song from the playlist?')) {
        return;
    }

    fetch(`/favlist/${playlistId}/`)
        .then(response => response.json())
        .then(favlistData => {
            const existingSongs = favlistData.songs; 
            const updatedSongs = existingSongs.filter(id => id !== songId);

            fetch(`/favlist/${playlistId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ songs: updatedSongs }),
            })
            .then(response => {
                if (response.ok) {
                    const songItem = document.querySelector(`.song-item[data-song-id='${songId}']`);
                    if (songItem) {
                        songItem.remove();
                    }
                    alert('Song removed from playlist successfully.');
                } else {
                    throw new Error('Failed to remove song from playlist.');
                }
            })
            .catch(error => {
                console.error('Error updating playlist:', error);
                alert('An error occurred while removing the song from the playlist.');
            });
        })
        .catch(error => {
            console.error('Error fetching playlist data:', error);
            alert('An error occurred while removing the song from the playlist.');
        });
}

/**
 * Shows the favlist dropdown in the player area, allowing the user to add the currently playing song to a favlist.
 * @param {number|null} songId - The ID of the currently playing song.
 * @param {HTMLElement} buttonElement - The button element clicked.
 */
function showFavlistDropdownInPlayer(songId, buttonElement) {
    const existingDropdown = document.querySelector('.favlist-dropdown');
    if (existingDropdown) {
        existingDropdown.remove();
    }

    const dropdown = document.createElement('div');
    dropdown.classList.add('favlist-dropdown');

    document.body.appendChild(dropdown);

    accessibleFavlists.forEach(favlist => {
        const item = document.createElement('div');
        item.textContent = favlist.name;
        item.style.padding = '10px';
        item.style.cursor = 'pointer';
        item.addEventListener('click', () => {
            addSongToFavlist(favlist.id, songId);
            if (dropdown.parentNode) {
                dropdown.parentNode.removeChild(dropdown);
            }
        });
        dropdown.appendChild(item);
    });

    const rect = buttonElement.getBoundingClientRect();
    const dropdownRect = dropdown.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    let left = rect.right - dropdownRect.width + window.scrollX;
    let top = rect.top - dropdownRect.height + window.scrollY;

    if (top < window.scrollY) {
        top = rect.bottom + window.scrollY;
        if (top + dropdownRect.height > viewportHeight + window.scrollY) {
            top = viewportHeight + window.scrollY - dropdownRect.height;
        }
    }

    if (left < 0) {
        left = rect.left + window.scrollX;
        if (left + dropdownRect.width > viewportWidth + window.scrollX) {
            left = viewportWidth + window.scrollX - dropdownRect.width;
        }
    }

    dropdown.style.position = 'absolute';
    dropdown.style.left = `${left}px`;
    dropdown.style.top = `${top}px`;

    document.addEventListener('click', function onClickOutside(event) {
        if (!dropdown.contains(event.target) && event.target !== buttonElement) {
            if (dropdown.parentNode) {
                dropdown.parentNode.removeChild(dropdown);
            }
            document.removeEventListener('click', onClickOutside);
        }
    });
}

/**
 * Gets the currently playing song's data from the player or queue.
 * @returns {Object|null} The currently playing song object or null if not found.
 */
function getCurrentPlayingSong() {
    const audioPlayer = document.getElementById('audio-player');
    const titleElement = document.getElementById('track-title');
    const artistElement = document.getElementById('track-artist');
    const coverArt = document.getElementById('cover-art');

    const songUrl = audioPlayer.src;
    if (!songUrl) {
        return null;
    }

    const playlistItems = document.querySelectorAll('#playlist-container .queue-item');
    for (const item of playlistItems) {
        if (item.dataset.url === songUrl) {
            const songId = parseInt(item.dataset.songId);
            const songName = item.querySelector('.queue-title').textContent;
            const songArtist = item.querySelector('.queue-artist').textContent;
            const songCover = item.querySelector('.queue-image').src;

            return {
                id: songId,
                name: songName,
                author: songArtist,
                cover_url: songCover,
                mp3_url: songUrl
            };
        }
    }

    const songName = titleElement.textContent;
    const songArtist = artistElement.textContent;
    const songCover = coverArt.src;

    return {
        id: null, 
        name: songName,
        author: songArtist,
        cover_url: songCover,
        mp3_url: songUrl
    };
}
