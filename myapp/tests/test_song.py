from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from ..models import Song
from django_elasticsearch_dsl.test import ESTestCase
from ..documents import SongDocument
from elasticsearch_dsl import connections

User = get_user_model()

class SongAPIPermissionTests(APITestCase):
    def setUp(self):
        # Create a regular user
        self.user = User.objects.create_user(
            username='regular_user',
            password='pass1234',
            is_superuser=False
        )
        
        # Create a superuser
        self.superuser = User.objects.create_superuser(
            username='admin_user',
            password='adminpass1234'
        )
        
        # Create some sample songs
        self.song1 = Song.objects.create(
            name="Song One",
            author="Artist A",
            album="Album X",
            duration=300,
            lyrics="La la la ...",
            topics="topic1, topic2",
            mp3_url="http://example.com/song1.mp3",
            cover_url="http://example.com/cover1.jpg"
        )
        
        self.song2 = Song.objects.create(
            name="Song Two",
            author="SunoAI",
            album="Album Y",
            duration=250,
            lyrics="Do re mi ...",
            topics="topic2, topic3",
            mp3_url="http://example.com/song2.mp3",
            cover_url="http://example.com/cover2.jpg"
        )
        
        self.list_url = reverse('song-list-create')
        self.detail_url = reverse('song-detail', args=[self.song1.id])
        
        self.client = APIClient()
    
    def test_get_list_unauthenticated(self):
        # Unauthenticated requests should be able to GET
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_list_authenticated_regular_user(self):
        # Authenticated regular user should be able to GET
        self.client.login(username='regular_user', password='pass1234')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()
    
    def test_post_authenticated_regular_user(self):
        # Regular user should NOT be able to POST
        self.client.login(username='regular_user', password='pass1234')
        data = {
            "name": "New Song",
            "author": "New Artist",
            "album": "New Album",
            "duration": 200,
            "lyrics": "New lyrics...",
            "topics": "topicX",
            "mp3_url": "http://example.com/newsong.mp3",
            "cover_url": "http://example.com/newcover.jpg"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
    
    def test_post_superuser(self):
        # Superuser should be able to POST
        self.client.login(username='admin_user', password='adminpass1234')
        data = {
            "name": "Admin Song",
            "author": "Admin Artist",
            "album": "Admin Album",
            "duration": 200,
            "lyrics": "Admin lyrics...",
            "topics": "adminTopic",
            "mp3_url": "http://example.com/adminsong.mp3",
            "cover_url": "http://example.com/admincover.jpg"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()
    
    def test_put_regular_user(self):
        # Regular user cannot update an existing song
        self.client.login(username='regular_user', password='pass1234')
        data = {
            "name": "Song One Updated",
            "author": "Artist A",
            "album": "Album X",
            "duration": 300,
            "lyrics": "Updated lyrics...",
            "topics": "topic1, topic2",
            "mp3_url": "http://example.com/song1.mp3",
            "cover_url": "http://example.com/cover1.jpg"
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
    
    def test_put_superuser(self):
        # Superuser can update
        self.client.login(username='admin_user', password='adminpass1234')
        data = {
            "name": "Song One Updated by Admin",
            "author": "Artist A",
            "album": "Album X",
            "duration": 300,
            "lyrics": "Updated lyrics by admin",
            "topics": "topic1, topic2",
            "mp3_url": "http://example.com/song1.mp3",
            "cover_url": "http://example.com/cover1.jpg"
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()
    
    def test_delete_regular_user(self):
        # Regular user cannot delete
        self.client.login(username='regular_user', password='pass1234')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
    
    def test_delete_superuser(self):
        # Superuser can delete
        self.client.login(username='admin_user', password='adminpass1234')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.logout()


class SongSearchViewTests(ESTestCase, APITestCase):
    def setUp(self):
        super().setUp()
        connections.create_connection(alias='default', hosts=['localhost:9200'])
        
        # Create test data
        self.song1 = Song.objects.create(
            name="Pop Song",
            author="Artist A",
            album="Hit Album",
            duration=210,
            lyrics="Pop lyrics...",
            topics="pop, hits",
            mp3_url="http://example.com/popsong.mp3",
            cover_url="http://example.com/popcover.jpg"
        )
        
        self.song2 = Song.objects.create(
            name="AI Generated Track",
            author="SunoAI",
            album="AI Album",
            duration=180,
            lyrics="AI lyrics...",
            topics="ai, future",
            mp3_url="http://example.com/aitrack.mp3",
            cover_url="http://example.com/aicover.jpg"
        )
        
        # Index data
        SongDocument().update(Song.objects.all())

        self.search_url = reverse('song-search',)
        
        # Create a regular user to pass authentication
        self.user = User.objects.create_user(
            username='search_user',
            password='searchpass',
            is_superuser=False
        )
        
        self.client = APIClient()
        self.client.login(username='search_user', password='searchpass')

    def test_search_without_ai_param(self):
        # Should exclude songs by "SunoAI"
        response = self.client.get(self.search_url + '?search=Pop&limit=20')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The "Pop Song" by "Artist A" should appear
        self.assertEqual(response.data['count'], 1)
        self.assertIn('Pop Song', [r['name'] for r in response.data['results']])

    def test_search_with_ai_param_true(self):
        # ai=True means we do not exclude "SunoAI"
        response = self.client.get(self.search_url + '?search=AI&ai=True&limit=20')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Now "AI Generated Track" by "SunoAI" should appear
        self.assertEqual(response.data['count'], 1)
        self.assertIn('AI Generated Track', [r['name'] for r in response.data['results']])

    def test_search_by_specific_field(self):
        # Searching by a specific field that is allowed
        response = self.client.get(self.search_url + '?field=name&search=Pop&limit=20')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_by_invalid_field(self):
        # Searching by a non-existent field should return a 400 Bad Request
        response = self.client.get(self.search_url + '?field=invalidfield&search=Pop&limit=20')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not a valid search field", str(response.data))

