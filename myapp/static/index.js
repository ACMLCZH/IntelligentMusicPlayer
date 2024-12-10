let accessibleFavlists = [];
let currentPlaylistData = null;
let currentPlayQueue = null;
// Declare a global variable to hold the MusicPlayer instance
let player = null;
let currentAIData = null;

document.addEventListener('DOMContentLoaded', function() {
    // Load playlists
    fetchPlayLists();
    setupNavbar();

    // Initialize the MusicPlayer instance
    player = new MusicPlayer();

    // Click on a playlist to load its songs
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

    // Add to play queue button
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
    
    // Natural language play queue management
    document.getElementById('nlp-input').addEventListener('input', function () {
        this.style.height = 'auto'; 
        this.style.height = this.scrollHeight + 'px';
    });

    const nlpExamples = [
        "Shuffle my queue",
        "Play Summer Rain every two songs",
        "Play Jazz music",
    ];
    
    const nlpInput = document.getElementById('nlp-input');
    
    // Set initial random example
    let currentIndex = Math.floor(Math.random() * nlpExamples.length);
    nlpInput.placeholder = `You can say "${nlpExamples[currentIndex]}"`;
    
    // Rotate examples every 3 seconds
    setInterval(() => {
        currentIndex = (currentIndex + 1) % nlpExamples.length;
        nlpInput.placeholder = `You can say "${nlpExamples[currentIndex]}"`;
    }, 3000);

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
        if (currentAIData) {
            displayAIData();
        } else {
            generateSongsWithAI();
        }
    });

    // Add event listener for right-click on playlist items
    document.getElementById('playlist-list').addEventListener('contextmenu', function(e) {
        e.preventDefault();
        let target = e.target.closest('li');
        if (target) {
            showPlaylistContextMenu(e, target);
        }
    });

    // Add event listener for right-click on song items
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

    document.getElementById('add-to-playlist-btn').addEventListener('click', function(e) {

        e.stopPropagation(); // 防止事件冒泡
        const currentSong = getCurrentPlayingSong();
        if (currentSong) {
            showFavlistDropdownInPlayer(currentSong.id, this);
        } else {
        }
    });

    // Close the dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const dropdown = document.querySelector('.favlist-dropdown');
        if (dropdown && !dropdown.contains(e.target)) {
            dropdown.remove();
        }
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


    // Edit profile link
    // Delated
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
                displaySongs(data.results);

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


function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}


// Function to display search results
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

        // Double-click to play
        songItem.addEventListener('dblclick', () => {
            // Create a new queue with just this song
            currentPlayQueue = [{
                id: song.id,
                title: song.name,
                artist: song.author,
                cover: song.cover_url,
                url: song.mp3_url
            }];
            
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
                player.updatePlaylistItems();
                player.loadCurrentTrack();
            }
        });

        // Add to favlist button event
        const addButton = songItem.querySelector('.add-to-favlist-button');
        addButton.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent triggering parent events
            showFavlistDropdown(song.id, addButton);
        });

        songsList.appendChild(songItem);
    });
    
    const playlistCover = document.getElementById('playlist-cover');
    if (songs.length > 0) {
        // Select a random song
        const randomIndex = Math.floor(Math.random() * songs.length);
        const randomSong = songs[randomIndex];
        playlistCover.src = randomSong.cover_url;
    } else {
        playlistCover.src = '/static/default-cover.jpg';
    }
}


// Fetch playlists from the server
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
            accessibleFavlists = data.favlists_detail; // Store the playlists data
            displayPlayLists(data.favlists_detail, selectedPlaylistId);
        })
        .catch(error => {
            console.error('Error fetching playlists:', error);
        });
}

function displayPlayLists(playlists, selectedPlaylistId = null) {
    let playlistList = document.getElementById('playlist-list');
    playlistList.innerHTML = ''; // 清空现有的播放列表

    playlists.forEach(function(playlist) {
        let li = document.createElement('li');
        li.textContent = playlist.name; // 使用 Favlist 模型中的 `name`
        li.dataset.id = playlist.id;
        playlistList.appendChild(li);

        playlistList.style.userSelect = 'none';
    });

    // 自动选择并加载指定的播放列表，若未指定则选择第一个
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

// Fetch songs from a specific playlist
function fetchPlayList(playlistId) {
    fetch(`/favlist/${playlistId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            currentPlaylistData = data; // Store the data
            window.currentPlaylistData = currentPlaylistData;   // Expose it to the global scope
            displayPlayList(data);
        })
        .catch(error => {
            console.error('Error fetching playlists:', error);
        });
}

function displayPlayList(playListData) {
    // Show the playlist-info section
    document.querySelector('.playlist-info').style.display = 'flex';
    document.getElementById('current-playlist-title').textContent = playListData.name;
    document.getElementById('ai-generate-button').style.display = 'flex';
    document.getElementById('add-to-playqueue').style.display = 'flex';
    console.log(playListData);
    displaySongs(playListData.songs_detail);
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
    
    // Update player's playlist items
    if (player) {
        player.updatePlaylistItems();
    }
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

    if (songId === null) {
        alert('Cannot add current song to favlist.');
        return;
    }
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
        // Update the user's favlists and auto-select the new playlist
        updateUserFavlists(newFavlist.id);
        // Clear the input field and hide the dropdown
        document.getElementById('new-playlist-name').value = '';
        document.getElementById('add-playlist-dropdown').style.display = 'none';
        // Automatically select the newly created playlist


        // fetchPlaylists(newFavlist.id);
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

function generateSongsWithAI() {
    if (!currentPlaylistData || !currentPlaylistData.id) {
        alert('No playlist selected.');
        return;
    }

    const playlistId = currentPlaylistData.id;
    // console.log(`Generating songs for playlist ID: ${playlistId}\n`);

    // Create an AbortController to allow canceling the request
    const controller = new AbortController();
    const signal = controller.signal;

    // Show loading spinner and disable UI
    // showLoadingSpinner(controller);

    // Send GET request to the generate-songs API
    const button = document.getElementById('ai-generate-button');
    button.disabled = true;
    // spinner.style.display = true;

    fetch(`/generate-songs/${playlistId}/`, { signal })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error generating songs: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            button.disabled = false;
            // button.querySelector("#spinner").style.display = 'none';

            // Display generated songs
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

function showPlaylistContextMenu(event, playlistItem) {
    closeContextMenus(); // Close any existing context menus

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

function showSongContextMenu(event, songItem) {
    closeContextMenus(); // Close any existing context menus

    // // 检查是否为搜索结果项
    // const songsList = document.getElementById('songs-list');
    // if (songsList.contains(songItem)) {
    //     console.log("Search results cannot be modified.");
    //     return; // 直接返回，不显示右键菜单
    // }

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


function closeContextMenus() {
    const existingMenus = document.querySelectorAll('.context-menu');
    existingMenus.forEach(menu => menu.remove());
}

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
            // Remove the playlist from the UI
            const playlistItem = document.querySelector(`#playlist-list li[data-id='${playlistId}']`);
            if (playlistItem) {
                playlistItem.remove();
            }
            // Optionally, clear the songs list if the deleted playlist was selected
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


function removeSongFromPlaylist(playlistId, songId) {
    if (!confirm('Are you sure you want to remove this song from the playlist?')) {
        return;
    }

    // Fetch the current playlist data to get the existing songs
    fetch(`/favlist/${playlistId}/`)
        .then(response => response.json())
        .then(favlistData => {
            const existingSongs = favlistData.songs; // Array of song IDs

            // Remove the song ID from the array
            const updatedSongs = existingSongs.filter(id => id !== songId);

            // Send PATCH request to update the playlist
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
                    // Remove the song from the UI
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
function showFavlistDropdownInPlayer(songId, buttonElement) {
    // 移除任何现有的下拉菜单
    const existingDropdown = document.querySelector('.favlist-dropdown');
    if (existingDropdown) {
        existingDropdown.remove();
    }

    // 创建下拉菜单元素
    const dropdown = document.createElement('div');
    dropdown.classList.add('favlist-dropdown');

    // 先将下拉菜单添加到文档中，以便计算尺寸
    document.body.appendChild(dropdown);

    // 创建每个收藏列表的选项
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

    // 获取按钮和下拉菜单的位置和尺寸
    const rect = buttonElement.getBoundingClientRect();
    const dropdownRect = dropdown.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // 首选位置（向左上方延展）
    let left = rect.right - dropdownRect.width + window.scrollX;
    let top = rect.top - dropdownRect.height + window.scrollY;

    // 如果下拉菜单超出顶部，则向下显示
    if (top < window.scrollY) {
        top = rect.bottom + window.scrollY;
        // 确保不会超出底部
        if (top + dropdownRect.height > viewportHeight + window.scrollY) {
            top = viewportHeight + window.scrollY - dropdownRect.height;
        }
    }

    // 如果下拉菜单超出左侧，则向右显示
    if (left < 0) {
        left = rect.left + window.scrollX;
        // 确保不会超出右侧
        if (left + dropdownRect.width > viewportWidth + window.scrollX) {
            left = viewportWidth + window.scrollX - dropdownRect.width;
        }
    }

    // 设置下拉菜单的位置
    dropdown.style.position = 'absolute';
    dropdown.style.left = `${left}px`;
    dropdown.style.top = `${top}px`;

    // 当点击其他地方时，关闭下拉菜单
    document.addEventListener('click', function onClickOutside(event) {
        if (!dropdown.contains(event.target) && event.target !== buttonElement) {
            if (dropdown.parentNode) {
                dropdown.parentNode.removeChild(dropdown);
            }
            document.removeEventListener('click', onClickOutside);
        }
    });
}


function getCurrentPlayingSong() {
    const audioPlayer = document.getElementById('audio-player');
    const titleElement = document.getElementById('track-title');
    const artistElement = document.getElementById('track-artist');
    const coverArt = document.getElementById('cover-art');

    // 获取当前播放的歌曲 URL
    const songUrl = audioPlayer.src;
    if (!songUrl) {
        return null;
    }

    // 从播放队列中查找匹配的歌曲信息
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

    // 如果未在播放队列中找到匹配项，使用播放器区域的信息
    const songName = titleElement.textContent;
    const songArtist = artistElement.textContent;
    const songCover = coverArt.src;

    return {
        id: null, // 如果无法获取歌曲 ID，可以设置为 null
        name: songName,
        author: songArtist,
        cover_url: songCover,
        mp3_url: songUrl
    };
}