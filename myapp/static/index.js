let accessibleFavlists = [];
let currentPlaylistData = null;
// Declare a global variable to hold the MusicPlayer instance
let player = null;

document.addEventListener('DOMContentLoaded', function() {
    // Load playlists
    fetchPlaylists();

    setupNavbar();

    // Initialize the MusicPlayer instance
    player = new MusicPlayer();

    // Click on a playlist to load its songs
    document.getElementById('playlist-list').addEventListener('click', function(e) {
        let target = e.target.closest('li');
        if (target) {
            let playlistId = target.dataset.id;
            console.log(`Fetching details for playlist ID: ${playlistId}`);
            fetchSongs(playlistId);

            let playlistItems = document.querySelectorAll('#playlist-list li');
            playlistItems.forEach(function(item) {
                item.classList.remove('active');
            });

            target.classList.add('active');

            document.getElementById('current-playlist-title').textContent = target.textContent;
            
        }
    });

    // Add to play queue button
    document.getElementById('add-to-playqueue').addEventListener('click', function() {
        const playQueue = document.getElementById('playlist-container');
        playQueue.innerHTML = currentPlaylistData.songs_detail.map((song, index) => `
            <li class="queue-item ${index === 0 ? 'active' : ''}" data-song-id="${song.id}" data-url="${song.mp3_url}">
                <img class="queue-image" src="${song.cover_url}" alt="Song Cover">
                <div class="queue-details">
                    <p class="queue-title">${song.name}</p>
                    <p class="queue-artist">${song.author}</p>
                </div>
            </li>
        `).join('');
    
        // Use the existing player instance
        if (player) {
            player.playlistItems = Array.from(playQueue.getElementsByTagName('li'));
            player.currentIndex = 0;
    
            // Update the player UI elements with the first song
            if (currentPlaylistData.songs_detail.length > 0) {
                const firstSong = currentPlaylistData.songs_detail[0];
                player.coverArt.src = firstSong.cover_url;
                player.titleElement.textContent = firstSong.name;
                player.artistElement.textContent = firstSong.author;
                player.audio.src = firstSong.mp3_url;
    
                // Play the first song
                player.audio.play();
            }
    
            player.updateNavigationButtons();
        }
    });

    // Natural language play queue management
    document.getElementById('nlp-input').addEventListener('input', function () {
        this.style.height = 'auto'; 
        this.style.height = this.scrollHeight + 'px';
    });

    document.getElementById('add-playlist-button').addEventListener('click', function() {
        toggleAddPlaylistDropdown();
    });

    // Add event listener to the create playlist button
    document.getElementById('create-playlist-button').addEventListener('click', function() {
        createNewPlaylist();
    });

    // Close the dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById('add-playlist-dropdown');
        const addButton = document.getElementById('add-playlist-button');
        if (!dropdown.contains(e.target) && e.target !== addButton) {
            dropdown.style.display = 'none';
        }
    });

    document.getElementById('ai-generate-button').addEventListener('click', function() {
        generateSongsWithAI();
    });
    
});

// Function to set up navigation bar interactions
function setupNavbar() {

    console.log('Setting up navbar');
    // Home link click event
    document.getElementById('home-link').addEventListener('click', function(e) {
        e.preventDefault();
        // Logic to reload or navigate to the homepage
        window.location.href = '/index';
    });

    // Search functionality
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

    // User avatar click event to toggle dropdown menu
    const userAvatar = document.getElementById('user-avatar');
    const navUser = document.querySelector('.nav-user');

    userAvatar.addEventListener('click', function() {
        navUser.classList.toggle('active');
    });

    // Click outside to close the dropdown menu
    document.addEventListener('click', function(e) {
        if (!navUser.contains(e.target)) {
            navUser.classList.remove('active');
        }
    });

    // Logout and Edit Profile actions
    document.getElementById('logout').addEventListener('click', function(e) {
        e.preventDefault();
        // Logic to log out the user
        logoutUser();
    });

    document.getElementById('edit-profile').addEventListener('click', function(e) {
        e.preventDefault();
        // Logic to navigate to the edit profile page
        console.log('Navigate to edit profile page');
    });
}

// Function to perform search
function performSearch(query) {
    console.log('Searching for:', query);

    // Hide the playlist-info section
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
                displaySearchResults(data.results);
            } else {
                console.error('Unexpected API response:', data);
                // Optionally display an error message to the user
                displayNoResults();
            }
        })
        .catch(error => {
            console.error('Error during search:', error);
        });
}


// Function to display search results
function displaySearchResults(songs) {
    const songsList = document.getElementById('songs-list');
    console.log(songs);

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
            <div class="song-duration">${song.duration}s</div>
            <div class="song-actions">
                <img class="add-to-favlist-button" src="/static/add.webp" alt="Add to Favlist">
            </div>
        `;

        songItem.style.userSelect = 'none';

        // Double-click to play
        songItem.addEventListener('dblclick', () => {
            playSong(song);
        });

        // Add to favlist button event
        const addButton = songItem.querySelector('.add-to-favlist-button');
        addButton.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent triggering parent events
            showFavlistDropdown(song.id, addButton);
        });

        songsList.appendChild(songItem);
    });
}


// Fetch playlists from the server
function fetchPlaylists() {
    fetch('/userfav/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
            
        })
        .then(data => {
            accessibleFavlists = data.favlists_detail; // Store the playlists data
            displayPlaylists(data.favlists_detail);
        })
        .catch(error => {
            console.error('Error fetching playlists:', error);
        });
}

function displayPlaylists(playlists) {
    let playlistList = document.getElementById('playlist-list');
    playlistList.innerHTML = ''; // Clear existing playlists

    playlists.forEach(function(playlist) {
        let li = document.createElement('li');
        li.textContent = playlist.name; // Use `name` from the Favlist model
        li.dataset.id = playlist.id;
        playlistList.appendChild(li);

        playlistList.style.userSelect = 'none';
    });

}

// Fetch songs from a specific playlist
function fetchSongs(playlistId) {
    // Show the playlist-info section
    document.querySelector('.playlist-info').style.display = 'flex';

    fetch(`/favlist/${playlistId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            currentPlaylistData = data; // Store the data
            displaySongs(data);
        })
        .catch(error => {
            console.error('Error fetching playlists:', error);
        });
}

function displaySongs(favListData) {
    const songsList = document.getElementById('songs-list');
    console.log(favListData);

    songsList.innerHTML = ''; // 清空之前的内容

    const songsDetail = favListData.songs_detail; // 提取 songs_detail 数据

    songsDetail.forEach((song, index) => {
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
            <div class="song-duration">${song.duration}s</div>
            <div class="song-actions">
                <img class="add-to-favlist-button" src="/static/add.webp" alt="Add to Favlist">
            </div>
        `;

        songItem.style.userSelect = 'none';

        // 双击播放
        songItem.addEventListener('dblclick', () => {
            playSong(song);
        });

        // 收藏按钮事件
        const addButton = songItem.querySelector('.add-to-favlist-button');
        addButton.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent triggering parent events
            showFavlistDropdown(song.id, addButton);
        });

        songsList.appendChild(songItem);
    });
    // Update player's playlist items
    if (player) {
        player.updatePlaylistItems();
    }

    const playlistCover = document.getElementById('playlist-cover');
    if (songsDetail.length > 0) {
        // Select a random song
        const randomIndex = Math.floor(Math.random() * songsDetail.length);
        const randomSong = songsDetail[randomIndex];
        playlistCover.src = randomSong.cover_url;
    } else {
        playlistCover.src = '/static/default-cover.jpg';
    }
}

// Play a song
function playSong(song) {
    // Update the play queue with the selected song
    const playQueue = document.getElementById('playlist-container');
    const songElement = `
        <li class="queue-item active" data-song-id="${song.id}" data-url="${song.mp3_url}">
            <img class="queue-image" src="${song.cover_url}" alt="Song Cover">
            <div class="queue-details">
                <p class="queue-title">${song.name}</p>
                <p class="queue-artist">${song.author}</p>
            </div>
        </li>
    `;
    playQueue.innerHTML = songElement;
    
    // Use the existing player instance
    if (player) {
        // Update the playlist items
        player.playlistItems = Array.from(playQueue.getElementsByTagName('li'));
        player.currentIndex = 0;
        
        // Update the player UI elements
        player.coverArt.src = song.cover_url;
        player.titleElement.textContent = song.name;
        player.artistElement.textContent = song.author;
        player.audio.src = song.mp3_url;
        
        // Play the song
        player.audio.play();
        
        // Update navigation buttons if necessary
        player.updateNavigationButtons();
    }
}

// Toggle favorite status of a song
function toggleCollection(songId, buttonElement) {
    // Logic to favorite/unfavorite a song
    console.log("Toggled favorite status for song ID:", songId);

    // Example: Update the button text (in a real app, you'd update the backend)
    let isFavorited = buttonElement.textContent === 'F';
    buttonElement.textContent = isFavorited ? 'U' : 'F';
}

// Update the play queue based on a natural language command
function updatePlayQueue(command) {
    // Send the command to the server and update the play queue
    console.log("Updating play queue with command:", command);
    // Simulate server response with a new play queue
    let newPlayQueue = [
        {"id": 8, "title": "New Song 1"},
        {"id": 9, "title": "New Song 2"}
    ];
    displayPlayQueue(newPlayQueue);
}

// Display the play queue
function displayPlayQueue(queue) {
    let playQueueList = document.getElementById('play-queue-list');
    playQueueList.innerHTML = ''; // Clear previous queue

    queue.forEach(function(song, index) {
        let li = document.createElement('li');
        li.textContent = (index === 0 ? "Now Playing: " : "") + song.title;
        playQueueList.appendChild(li);
    });
}


function showFavlistDropdown(songId, addButtonElement) {
    // Remove any existing dropdowns
    const existingDropdown = document.querySelector('.favlist-dropdown');
    if (existingDropdown) {
        existingDropdown.parentNode.removeChild(existingDropdown);
    }

    // Create a dropdown menu element
    const dropdown = document.createElement('div');
    dropdown.classList.add('favlist-dropdown');

    // Get the position of the addButtonElement
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

    // Create list items for each favlist
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

    // Append the dropdown to the body
    document.body.appendChild(dropdown);

    // Close the dropdown when clicking outside
    document.addEventListener('click', function onClickOutside(event) {
        if (!dropdown.contains(event.target) && event.target !== addButtonElement) {
            if (dropdown.parentNode) {
                dropdown.parentNode.removeChild(dropdown);
            }
            document.removeEventListener('click', onClickOutside);
        }
    });
}

function addSongToFavlist(favlistId, songId) {
    // Fetch the existing songs in the favlist
    fetch(`/favlist/${favlistId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(favlistData => {
            // Get existing song IDs
            let existingSongs = favlistData.songs; // Assuming 'songs' is an array of song IDs

            // Add the new song ID if not already in the list
            if (!existingSongs.includes(songId)) {
                existingSongs.push(songId);
            } else {
                console.log('Song already in the favlist');
                return;
            }

            // Send PATCH request to update the favlist
            fetch(`/favlist/${favlistId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken() // Include CSRF token
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
                // Optionally, show a success message to the user
            })
            .catch(error => {
                console.error('Error adding song to favlist:', error);
                // Optionally, show an error message to the user
            });
        })
        .catch(error => {
            console.error('Error fetching favlist data:', error);
        });
}


function toggleAddPlaylistDropdown() {
    const dropdown = document.getElementById('add-playlist-dropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
}

function createNewPlaylist() {
    const playlistNameInput = document.getElementById('new-playlist-name');
    const playlistName = playlistNameInput.value.trim();
    if (playlistName === '') {
        alert('Please enter a playlist name.');
        return;
    }

    // Call function to create the playlist
    postNewFavlist(playlistName);
}

function postNewFavlist(playlistName) {
    fetch('/favlist/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken() // Include CSRF token
        },
        body: JSON.stringify({
            name: playlistName,
            songs: [] // Start with an empty list of songs
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
        // Update the user's favlists
        updateUserFavlists(newFavlist.id);
        // Clear the input field and hide the dropdown
        document.getElementById('new-playlist-name').value = '';
        document.getElementById('add-playlist-dropdown').style.display = 'none';
    })
    .catch(error => {
        console.error('Error creating new favlist:', error);
        alert('Error creating playlist. Please try again.');
    });
}

function updateUserFavlists(newFavlistId) {
    // First, fetch the current favlists of the user
    fetch('/userfav/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error fetching user favlists: ' + response.statusText);
            }
            return response.json();
        })
        .then(userFavData => {
            // Get existing favlist IDs
            let existingFavlists = userFavData.favlists;

            // Add the new favlist ID if not already in the list
            if (!existingFavlists.includes(newFavlistId)) {
                existingFavlists.push(newFavlistId);
            }

            // Send PATCH request to update the user's favlists
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
                // Refresh the playlists display
                fetchPlaylists();
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

function logoutUser() {
    fetch('/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken() // Use your existing getCSRFToken function
        }
    })
    .then(response => {
        if (response.ok) {
            // Logout was successful
            window.location.href = '/login/'; // Redirect to the login page
        } else {
            throw new Error('Logout failed.');
        }
    })
    .catch(error => {
        console.error('Error during logout:', error);
        alert('An error occurred during logout. Please try again.');
    });
}

function generateSongsWithAI() {
    if (!currentPlaylistData || !currentPlaylistData.id) {
        alert('No playlist selected.');
        return;
    }

    const playlistId = currentPlaylistData.id;

    // console.log(`Generating songs for playlist ID: ${playlistId}`);

    // Create an AbortController to allow canceling the request
    const controller = new AbortController();
    const signal = controller.signal;

    // Show loading spinner and disable UI
    showLoadingSpinner(controller);

    // Send GET request to the generate-songs API
    fetch(`/generate-songs/${playlistId}/`, { signal })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error generating songs: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            // Hide loading spinner and enable UI
            hideLoadingSpinner();

            // Display generated songs
            if (Array.isArray(data)) {
                displaySearchResults(data);
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
            // Hide loading spinner and enable UI
            hideLoadingSpinner();
        });
}

function showLoadingSpinner(controller) {
    // Create overlay
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

    // Create spinner
    const spinner = document.createElement('div');
    spinner.classList.add('spinner');

    // Create cancel button
    const cancelButton = document.createElement('button');
    cancelButton.textContent = 'Cancel';
    cancelButton.style.marginTop = '20px';
    cancelButton.style.padding = '10px 20px';
    cancelButton.style.fontSize = '16px';
    cancelButton.style.cursor = 'pointer';
    cancelButton.addEventListener('click', function() {
        controller.abort(); // Abort the fetch request
        hideLoadingSpinner();
    });

    overlay.appendChild(spinner);
    overlay.appendChild(cancelButton);

    document.body.appendChild(overlay);
}

function hideLoadingSpinner() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        document.body.removeChild(overlay);
    }
}