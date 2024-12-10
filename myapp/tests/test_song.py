from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Song
from ..documents import SongDocument
from elasticsearch_dsl import Search

class SongModelTestCase(TestCase):
    def setUp(self):
        self.song = Song.objects.create(
            name="Test Song",
            author="Test Author",
            album="Test Album",
            duration=300,
            lyrics="These are the lyrics of the test song.",
            topics="Pop, Rock",
            mp3_url="http://example.com/test.mp3",
            cover_url="http://example.com/test.jpg",
        )

    def test_song_str_representation(self):
        self.assertEqual(str(self.song), "Test Song")

    def test_song_creation(self):
        self.assertEqual(Song.objects.count(), 1)

class SongListCreateAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.song_data = {
            "name": "Test Song",
            "author": "Test Author",
            "album": "Test Album",
            "duration": 300,
            "lyrics": "These are the lyrics of the test song.",
            "topics": "Pop, Rock",
            "mp3_url": "http://example.com/test.mp3",
            "cover_url": "http://example.com/test.jpg",
        }
        self.song = Song.objects.create(**self.song_data)

    def test_list_songs(self):
        response = self.client.get("/songs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_song(self):
        response = self.client.post("/songs/", self.song_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Song.objects.count(), 2)

class SongRetrieveUpdateDestroyAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.song = Song.objects.create(
            name="Test Song",
            author="Test Author",
            album="Test Album",
            duration=300,
            lyrics="These are the lyrics of the test song.",
            topics="Pop, Rock",
            mp3_url="http://example.com/test.mp3",
            cover_url="http://example.com/test.jpg",
        )

    def test_retrieve_song(self):
        response = self.client.get(f"/songs/{self.song.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Song")

    def test_update_song(self):
        data = {"name": "Updated Test Song"}
        response = self.client.patch(f"/songs/{self.song.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.song.refresh_from_db()
        self.assertEqual(self.song.name, "Updated Test Song")

    def test_delete_song(self):
        response = self.client.delete(f"/songs/{self.song.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Song.objects.count(), 0)
