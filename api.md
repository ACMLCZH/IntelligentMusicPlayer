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
        "duration": 183,
        "lyrics": "Imagine all the people...",
        "url": "http://example.com/song1"
    },
    {
        "id": 2,
        "name": "Bohemian Rhapsody",
        "author": "Queen",
        "duration": 354,
        "lyrics": "Is this the real life? Is this just fantasy?",
        "url": "http://example.com/song2"
    }
]
```

#### Endpoint: `POST /song/`  
##### Example Request:
```json
{
    "name": "Hey Jude",
    "author": "The Beatles",
    "duration": 430,
    "lyrics": "Hey Jude, don't make it bad...",
    "url": "http://example.com/heyjude"
}
```

##### Example Response:
```json
{
    "id": 3,
    "name": "Hey Jude",
    "author": "The Beatles",
    "duration": 430,
    "lyrics": "Hey Jude, don't make it bad...",
    "url": "http://example.com/heyjude"
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
    "duration": 183,
    "lyrics": "Imagine all the people...",
    "url": "http://example.com/song1"
}
```

#### Endpoint: `PUT /song/<int:pk>/`
##### Example Request:
```json
{
    "name": "Imagine",
    "author": "John Lennon",
    "duration": 200,
    "lyrics": "Imagine all the people living life in peace...",
    "url": "http://example.com/song1-updated"
}
```

##### Example Response:
```json
{
    "id": 1,
    "name": "Imagine",
    "author": "John Lennon",
    "duration": 200,
    "lyrics": "Imagine all the people living life in peace...",
    "url": "http://example.com/song1-updated"
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
##### Example Request:
```http
GET http://localhost:8000/song/search/?search=Imagine
```

##### Example Response:
```json
[
    {
        "id": 1,
        "name": "Imagine",
        "author": "John Lennon",
        "duration": 183,
        "lyrics": "Imagine all the people...",
        "url": "http://example.com/song1"
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
    "songs": [1, 2]
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
        "id": 1,
        "user": 1,
        "favlists": [1, 2]
    }
]
```

#### Endpoint: `POST /userfav/`
##### Example Request:
```json
{
    "favlists": [1]
}
```

##### Example Response:
```json
{
    "id": 2,
    "user": 1,
    "favlists": [1]
}
```

---

### 7. **User Favorites Retrieve/Update/Delete API**
#### Endpoint: `GET /userfav/<int:pk>/`
##### Example Request:
```http
GET http://localhost:8000/userfav/1/
Authorization: Bearer <JWT_TOKEN>
```

##### Example Response:
```json
{
    "id": 1,
    "user": 1,
    "favlists": [1, 2]
}
```

#### Endpoint: `PUT /userfav/<int:pk>/`
##### Example Request:
```json
{
    "favlists": [2]
}
```

##### Example Response:
```json
{
    "id": 1,
    "user": 1,
    "favlists": [2]
}
```

#### Endpoint: `DELETE /userfav/<int:pk>/`
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
