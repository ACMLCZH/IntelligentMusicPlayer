from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from myapp.models import Song, Favlist


class FavlistAPITestCase(TestCase):
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpass1"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpass2"
        )

        # Create some songs to use in favlists
        self.song1 = Song.objects.create(
            name="Song One",
            author="Author A",
            album="Album A",
            duration=200,
            lyrics="La la la",
            topics="topic1,topic2",
            mp3_url="http://example.com/song1.mp3",
            cover_url="http://example.com/cover1.jpg",
        )
        self.song2 = Song.objects.create(
            name="Song Two",
            author="Author B",
            album="Album B",
            duration=300,
            lyrics="Do re mi",
            topics="topic2,topic3",
            mp3_url="http://example.com/song2.mp3",
            cover_url="http://example.com/cover2.jpg",
        )

        self.client = APIClient()
        self.favlist_url = "/favlist/"

    def test_create_favlist_unauthenticated(self):
        # Attempt to create favlist without authentication
        data = {"name": "My Favlist", "songs": [self.song1.id, self.song2.id]}
        response = self.client.post(self.favlist_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_favlist_authenticated(self):
        # Authenticate and create a new favlist
        self.client.force_authenticate(user=self.user1)
        data = {"name": "My Favlist", "songs": [self.song1.id, self.song2.id]}
        response = self.client.post(self.favlist_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "My Favlist")
        self.assertEqual(response.data["owner"], "testuser1")

    def test_retrieve_favlist_authenticated(self):
        # Create a favlist for user1
        favlist = Favlist.objects.create(name="User1 Favlist", owner=self.user1)
        favlist.songs.set([self.song1, self.song2])

        # Attempt to retrieve with no auth
        detail_url = f"/favlist/{favlist.id}/"
        response = self.client.get(detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticate as user1 and retrieve
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "User1 Favlist")
        self.assertIn("songs_detail", response.data)
        self.assertEqual(len(response.data["songs_detail"]), 2)

    def test_update_favlist_as_owner(self):
        # Create favlist for user1
        favlist = Favlist.objects.create(name="Old Name", owner=self.user1)

        detail_url = f"/favlist/{favlist.id}/"

        # Update without auth
        response = self.client.put(
            detail_url, {"name": "New Name", "songs": []}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Auth as user1
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(
            detail_url, {"name": "New Name", "songs": []}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Name")

    def test_update_favlist_as_non_owner(self):
        # Create favlist for user1
        favlist = Favlist.objects.create(name="User1 Favlist", owner=self.user1)
        detail_url = f"/favlist/{favlist.id}/"

        # Auth as user2 (not the owner)
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(
            detail_url, {"name": "Hacked Name", "songs": []}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_favlist_as_owner(self):
        # Create favlist for user1
        favlist = Favlist.objects.create(name="Favlist to Delete", owner=self.user1)
        detail_url = f"/favlist/{favlist.id}/"

        # Auth as user1 and delete
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favlist.objects.filter(id=favlist.id).exists())

    def test_delete_favlist_as_non_owner(self):
        # Create favlist for user1
        favlist = Favlist.objects.create(
            name="Favlist Owned by User1", owner=self.user1
        )
        detail_url = f"/favlist/{favlist.id}/"

        # Auth as user2 (not the owner) and attempt to delete
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Favlist.objects.filter(id=favlist.id).exists())
