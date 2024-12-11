from django.test import TestCase, AsyncClient
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Song, Favlist
from ..views import get_playlist_from_api, _create_json_response
from django.http import JsonResponse
import json
import asyncio
from asgiref.sync import sync_to_async
from unittest.mock import patch, MagicMock
import uuid


class ViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.filter(username__startswith="testuser_").delete()

    async def asyncSetUp(self):
        unique_suffix = str(uuid.uuid4())[:8]
        self.test_username = f"testuser_{unique_suffix}"

        self.user = await sync_to_async(User.objects.create_user)(
            username=self.test_username, password="testpassword"
        )

        self.song1 = await sync_to_async(Song.objects.create)(
            name="Test Song 1",
            author="Test Author 1",
            album="Test Album 1",
            duration=200,
            lyrics="Test lyrics 1",
            topics="test,topic1",
            mp3_url="http://example.com/song1.mp3",
            cover_url="http://example.com/cover1.jpg",
        )

        self.song2 = await sync_to_async(Song.objects.create)(
            name="Test Song 2",
            author="Test Author 2",
            album="Test Album 2",
            duration=180,
            lyrics="Test lyrics 2",
            topics="test,topic2",
            mp3_url="http://example.com/song2.mp3",
            cover_url="http://example.com/cover2.jpg",
        )

        # Create test playlist
        self.favlist = await sync_to_async(Favlist.objects.create)(
            name="Test Playlist", owner=self.user
        )
        await sync_to_async(self.favlist.songs.add)(self.song1, self.song2)

        self.client = AsyncClient()
        # Force CSRF checks off for testing
        await sync_to_async(self.client.force_login)(self.user)

    def setUp(self):
        asyncio.run(self.asyncSetUp())

    def test_get_playlist_from_api(self):
        playlist = get_playlist_from_api(self.favlist.id)
        self.assertEqual(len(playlist), 2)
        self.assertEqual(playlist[0]["id"], self.song1.id)
        self.assertEqual(playlist[0]["title"], self.song1.name)
        self.assertEqual(playlist[0]["artist"], self.song1.author)
        self.assertEqual(playlist[0]["cover"], self.song1.cover_url)
        self.assertEqual(playlist[0]["url"], self.song1.mp3_url)

    def test_create_json_response(self):
        data = {"test": "data"}
        response = _create_json_response(data)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), data)

        response = _create_json_response(data, status=400)
        self.assertEqual(response.status_code, 400)

    @patch("myapp.views.get_playlist_from_api")
    @patch("myapp.views.sync_to_async")
    async def test_play_music(self, mock_sync_to_async, mock_get_playlist):
        # Setup mock playlist
        mock_playlist = [
            {
                "id": self.song1.id,
                "title": self.song1.name,
                "artist": self.song1.author,
                "cover": self.song1.cover_url,
                "url": self.song1.mp3_url,
            }
        ]

        # Setup mock for sync_to_async to return the wrapped function
        def mock_wrapper(func):
            async def wrapped(*args, **kwargs):
                # Call the original mocked function and return its result
                return func(*args, **kwargs)

            return wrapped

        mock_sync_to_async.side_effect = mock_wrapper
        mock_get_playlist.return_value = mock_playlist

        # Prepare request data
        data = {"playlist_id": str(self.favlist.id), "track_index": 0}

        # Make request
        response = await self.client.post(
            "/api/play-music/", data=json.dumps(data), content_type="application/json"
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["playlist"], mock_playlist)
        self.assertEqual(response_data["current_index"], 0)

        # Verify mock was called correctly
        mock_get_playlist.assert_called_once_with(str(self.favlist.id))

    @patch("myapp.views.PlaylistOrganizer")
    async def test_reorganize_playlist(self, mock_organizer_class):
        # Setup mock playlist
        mock_playlist = [
            {
                "id": self.song1.id,
                "title": self.song1.name,
                "artist": self.song1.author,
                "cover": self.song1.cover_url,
                "url": self.song1.mp3_url,
            }
        ]

        # Configure mock
        mock_instance = MagicMock()

        async def async_reorganize(*args, **kwargs):
            return mock_playlist

        mock_instance.reorganize_playlist = async_reorganize
        mock_organizer_class.return_value = mock_instance

        data = {"instruction": "shuffle the playlist", "queue": mock_playlist}

        response = await self.client.post(
            "/api/reorganize-playlist/",  # Update path to match urls.py
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data["status"], "success")
        self.assertEqual(response_data["playlist"], mock_playlist)

    @classmethod
    def tearDownClass(cls):
        User.objects.filter(username__startswith="testuser_").delete()
        super().tearDownClass()
