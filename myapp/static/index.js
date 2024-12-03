let accessibleFavlists = [];

document.addEventListener('DOMContentLoaded', function() {
    // Load playlists
    fetchPlaylists();

    setupNavbar();

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
        // Logic to add the current playlist to the play queue
        console.log("Add to Play Queue clicked");
    });

    // Natural language play queue management
    document.getElementById('nlp-button').addEventListener('click', function() {
        let command = document.getElementById('nlp-input').value;
        updatePlayQueue(command);
    });

    document.getElementById('nlp-input').addEventListener('input', function () {
        this.style.height = 'auto'; 
        this.style.height = this.scrollHeight + 'px';
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
        console.log('User logged out');
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
    // Implement your search logic here
    // For example, make an API call to your server to fetch search results
    // fetch(`/api/search?q=${encodeURIComponent(query)}`)
    //     .then(response => response.json())
    //     .then(data => {
    //         // Display search results
    //     })
    //     .catch(error => {
    //         console.error('Error during search:', error);
    //     });
}

// Fetch playlists from the server
function fetchPlaylists() {
    fetch('/favlist/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            accessibleFavlists = data; // Store the playlists data
            displayPlaylists(data);
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
    });
}

// Fetch songs from a specific playlist
function fetchSongs(playlistId) {
    // Replace this with an actual fetch call to your Django backend
    // Example:
    // fetch(`/api/playlists/${playlistId}/songs/`)
    //     .then(response => response.json())
    //     .then(data => displaySongs(data))
    //     .catch(error => console.error('Error fetching songs:', error));

    // Simulated server response based on playlistId
    fetch(`/favlist/${playlistId}`) // 根据 ID 获取收藏列表
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json(); // 解析为 JSON
    })
    .then(data => {
        displaySongs(data); // 调用 displaySongs，传入完整的响应数据
        // Update play queue
        if (data.songs_detail && data.songs_detail.length > 0) {
            const firstSong = data.songs_detail[0];
            
            // Update play queue
            const playQueue = document.getElementById('playlist-container');
            playQueue.innerHTML = data.songs_detail.map((song, index) => `
                <li data-song-id="${song.id}" ${index === 0 ? 'class="active"' : ''}>
                    <button class="song-select"
                        data-url="${song.mp3_url}"
                        data-cover="${song.cover_url}"
                        data-title="${song.name}"
                        data-artist="${song.author}">
                        <i class="fas fa-music"></i> ${song.name} - ${song.author}
                    </button>
                </li>
            `).join('');

            // Update player area
            document.querySelector('.player-container').innerHTML = `
                <img src="${firstSong.cover_url}" alt="Album Cover" class="cover-art" id="cover-art">
                <div class="player-info">
                    <h2 id="track-title">${firstSong.name}</h2>
                    <h3 id="track-artist">${firstSong.author}</h3>
                </div>
                <audio id="audio-player" controls>
                    <source src="${firstSong.mp3_url}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
                <div class="controls">
                    <button id="prev-btn">
                        <i class="fas fa-step-backward"></i> Previous
                    </button>
                    <button id="next-btn">
                        Next <i class="fas fa-step-forward"></i>
                    </button>
                </div>
            `;

            // Initialize player after updating DOM
            const player = new MusicPlayer();
            
            // // Start playing first song
            // const firstButton = playQueue.querySelector('.song-select');
            // if (firstButton) {
            //     player.loadTrack(firstButton, 0);
            // }
        }
    })
    .catch(error => {
        console.error('Error fetching playlists:', error); // 打印错误信息
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
}

// Play a song
function playSong(song) {
    // Create the audio player UI if it doesn't exist
    const playQueue = document.getElementById('playlist-container');
    
    // Add the song to play queue
    const songElement = `
        <li data-song-id="${song.id}" class="active">
            <button class="song-select"
                data-url="${song.mp3_url}"
                data-cover="${song.cover_url}"
                data-title="${song.name}"
                data-artist="${song.author}">
                <i class="fas fa-music"></i> ${song.name} - ${song.author}
            </button>
        </li>
    `;
    playQueue.innerHTML = songElement;

    // Update player UI
    document.querySelector('.player-container').innerHTML = `
        <img src="${song.cover_url}" alt="Album Cover" class="cover-art" id="cover-art">
        <div class="player-info">
            <h2 id="track-title">${song.name}</h2>
            <h3 id="track-artist">${song.author}</h3>
        </div>
        <audio id="audio-player" controls>
            <source src="${song.mp3_url}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
        <div class="controls">
            <button id="prev-btn">
                <i class="fas fa-step-backward"></i> Previous
            </button>
            <button id="next-btn">
                Next <i class="fas fa-step-forward"></i>
            </button>
        </div>
    `;

    // Initialize player and start playing
    const player = new MusicPlayer();
    const songButton = playQueue.querySelector('.song-select');
    if (songButton) {
        player.loadTrack(songButton, 0);
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
    console.log(`Adding song ID ${songId} to favlist ID ${favlistId}`);
}