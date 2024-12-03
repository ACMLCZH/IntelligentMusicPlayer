Below are examples of **requests** and **responses** for each of the APIs defined in your Django project. I'll assume your API is hosted at `http://localhost:8000/`.

---

### 1. **Song List and Create API**
#### Endpoint: `GET /song/`  
##### Example Request:
```http
GET http://localhost:8000/song/
```

##### Example Response:
```json
[
    {
        "id": 1,
        "name": "Imagine",
        "author": "John Lennon",
        "album": "example album",
        "duration": 183,
        "lyrics": "Imagine all the people...",
        "topics": "Peace, Unity, Hope",
        "mp3_url": "http://example.com/song1",
        "cover_url": "http://example.com/images/imagine_cover.jpg"
    },
    {
        "id": 2,
        "name": "Bohemian Rhapsody",
        "author": "Queen",
        "album": "example album",
        "duration": 354,
        "lyrics": "Is this the real life? Is this just fantasy?",
        "topics": "Drama, Emotion, Storytelling",
        "mp3_url": "http://example.com/song2",
        "cover_url": "http://example.com/images/bohemian_rhapsody_cover.jpg"
    }
]
```

#### Endpoint: `POST /song/`  
##### Example Request:
```json
{
    "name": "Hey Jude",
    "author": "The Beatles",
    "album": "example album",
    "duration": 430,
    "lyrics": "Hey Jude, don't make it bad...",
    "topics": "Encouragement, Love, Friendship",
    "mp3_url": "http://example.com/heyjude",
    "cover_url": "http://example.com/images/hey_jude_cover.jpg"
}
```

##### Example Response:
```json
{
    "id": 3,
    "name": "Hey Jude",
    "author": "The Beatles",
    "album": "example album",
    "duration": 430,
    "lyrics": "Hey Jude, don't make it bad...",
    "topics": "Encouragement, Love, Friendship",
    "mp3_url": "http://example.com/heyjude",
    "cover_url": "http://example.com/images/hey_jude_cover.jpg"
}
```

---

### 2. **Song Retrieve/Update/Delete API**
#### Endpoint: `GET /song/<int:pk>/`  
##### Example Request:
```http
GET http://localhost:8000/song/1/
```

##### Example Response:
```json
{
    "id": 1,
    "name": "Imagine",
    "author": "John Lennon",
    "album": "example album",
    "duration": 183,
    "lyrics": "Imagine all the people...",
    "topics": "Peace, Humanity, Hope",
    "mp3_url": "http://example.com/song1",
    "cover_url": "http://example.com/song1-cover.jpg"
}
```

#### Endpoint: `PUT /song/<int:pk>/`
##### Example Request:
```json
{
    "name": "Imagine",
    "author": "John Lennon",
    "album": "example album",
    "duration": 200,
    "lyrics": "Imagine all the people living life in peace...",
    "topics": "Peace, Humanity, Hope",
    "mp3_url": "http://example.com/song1-updated",
    "cover_url": "http://example.com/song1-cover-updated.jpg"
}
```

##### Example Response:
```json
{
    "id": 1,
    "name": "Imagine",
    "author": "John Lennon",
    "album": "example album",
    "duration": 200,
    "lyrics": "Imagine all the people living life in peace...",
    "topics": "Peace, Humanity, Hope",
    "mp3_url": "http://example.com/song1-updated",
    "cover_url": "http://example.com/song1-cover-updated.jpg"
}
```

#### Endpoint: `DELETE /song/<int:pk>/`
##### Example Request:
```http
DELETE http://localhost:8000/song/1/
```

##### Example Response:
```json
{
    "detail": "Song deleted successfully."
}
```

---

### 3. **Song Search API**
#### Endpoint: `GET /song/search/`

search=keyword
limit=X
##### Example Request:
```http
GET http://localhost:8000/song/search/?search=Imagine&limit=20
```

##### Example Response:
```json
[
    {
        "id": 1,
        "name": "Imagine",
        "author": "John Lennon",
        "album": "example album",
        "duration": 183,
        "lyrics": "Imagine all the people...",
        "topics": "Peace, Humanity, Hope",
        "mp3_url": "http://example.com/song1",
        "cover_url": "http://example.com/song1-cover.jpg"
    }
]
```

---

### 4. **Favlist List and Create API**
#### Endpoint: `GET /favlist/`
##### Example Request:
```http
GET http://localhost:8000/favlist/
```

##### Example Response:
```json
[
    {
        "id": 1,
        "name": "Chill Vibes",
        "songs": [1, 2]
    }
]
```

#### Endpoint: `POST /favlist/`
##### Example Request:
```json
{
    "name": "Workout Jams",
    "songs": [2, 3]
}
```

##### Example Response:
```json
{
    "id": 2,
    "name": "Workout Jams",
    "songs": [2, 3]
}
```

---

### 5. **Favlist Retrieve/Update/Delete API**
#### Endpoint: `GET /favlist/<int:pk>/`
##### Example Request:
```http
GET http://localhost:8000/favlist/1/
```

##### Example Response:
```json
{
    "id": 1,
    "name": "Chill Vibes",
    "songs": [1, 2],
    "songs_detail": [
        {
            "id": 1,
            "name": "Imagine",
            "author": "John Lennon",
            "album": "example album",
            "duration": 183,
            "lyrics": "Imagine all the people...",
            "topics": "Peace, Unity, Hope",
            "mp3_url": "http://example.com/song1",
            "cover_url": "http://example.com/images/imagine_cover.jpg"
        },
        {
            "id": 2,
            "name": "Bohemian Rhapsody",
            "author": "Queen",
            "album": "example album",
            "duration": 354,
            "lyrics": "Is this the real life? Is this just fantasy?",
            "topics": "Drama, Emotion, Storytelling",
            "mp3_url": "http://example.com/song2",
            "cover_url": "http://example.com/images/bohemian_rhapsody_cover.jpg"
        }
    ]
}
```

#### Endpoint: `PUT /favlist/<int:pk>/`
##### Example Request:
```json
{
    "name": "Evening Relaxation",
    "songs": [1]
}
```

##### Example Response:
```json
{
    "id": 1,
    "name": "Evening Relaxation",
    "songs": [1]
}
```

partially modify:
#### Endpoint: `PATCH /favlist/<int:pk>/`
##### Example Request:
```json
{
    "name": "PATCH",
}
```

##### Example Response:
```json
{
    "id": 1,
    "name": "PATCH",
    "songs": [1]
}
```

##### Example Request:
```json
{
    "songs": [1, 2],
}
```

##### Example Response:
```json
{
    "id": 1,
    "name": "PATCH",
    "songs": [1, 2]
}
```

#### Endpoint: `DELETE /favlist/<int:pk>/`
##### Example Request:
```http
DELETE http://localhost:8000/favlist/1/
```

##### Example Response:
```json
{
    "detail": "Favlist deleted successfully."
}
```

---

### 6. **User Favorites List and Create API**
#### Endpoint: `GET /userfav/`
##### Example Request:
```http
GET http://localhost:8000/userfav/
Authorization: Bearer <JWT_TOKEN>
```

##### Example Response:
```json
[
    {
        "user": 1,
        "favlists": [1, 2]
    }
]
```

#### Endpoint: `POST /userfav/` (Deprecated)
##### Example Request:
```json
{
    "favlists": [1]
}
```

##### Example Response:
```json
{
    "user": 1,
    "favlists": [1]
}
```

---

### 7. **User Favorites Retrieve/Update/Delete API**

partially modify:
#### Endpoint: `PATCH /userfav/`
##### Example Request:
```json
{
    "favlists": [2]
}
```

##### Example Response:
```json
{
    "user": 1,
    "favlists": [2]
}
```

#### Endpoint: `DELETE /userfav/`
##### Example Request:
```http
DELETE http://localhost:8000/userfav/1/
Authorization: Bearer <JWT_TOKEN>
```

##### Example Response:
```json
{
    "detail": "User favorites deleted successfully."
}
```


#### test

```
curl -X POST http://localhost:8000/userfav/ ^
-H "Content-Type: application/json" ^
-d "{\"favlists\": [2, 3]}" ^
--user "heaplax"
```

```
curl -X PUT http://localhost:8000/userfav/ ^
-H "Content-Type: application/json" ^
-d "{\"favlists\": [2]}" ^
--user "heaplax"
```