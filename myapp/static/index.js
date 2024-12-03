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
    // Make an HTTP GET request to your Django API endpoint
    fetch('/favlist/') // Replace with the correct URL for your Favlist API
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json(); // Parse the JSON response
        })
        .then(data => {
            displayPlaylists(data); // Pass the fetched data to displayPlaylists
        })
        .catch(error => {
            console.error('Error fetching playlists:', error); // Log any errors
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
                <button class="collection-button">F</button>
            </div>
        `;

        // 双击播放
        songItem.addEventListener('dblclick', () => {
            playSong(song);
        });

        // 收藏按钮事件
        songItem.querySelector('.collection-button').addEventListener('click', (e) => {
            e.stopPropagation(); // 防止触发 dblclick 事件
            toggleCollection(song.id, e.target);
        });

        songsList.appendChild(songItem);
    });
}

// Play a song
function playSong(song) {
    // Logic to play the song
    console.log("Now playing:", song.title);
    // Update Player Area (optional)
    document.querySelector('.player-area').innerHTML = `
        <p>Now Playing:</p>
        <h3>${song.title}</h3>
        <p>${song.artist} - ${song.album}</p>
    `;
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


