from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from myapp.models import Song, Favlist

class GenerateSongsViewTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='testpass1')
        self.song1 = Song.objects.create(
            name="Juicy",
            author="The Notorious B.I.G.",
            album="Ready to Die",
            duration=200,
            lyrics='La la la',
            topics='topic1,topic2',
            mp3_url='http://example.com/song1.mp3',
            cover_url='http://example.com/cover1.jpg'
        )
        self.song2 = Song.objects.create(
            name="Lose Yourself",
            author="Eminem",
            album="8 Mile Soundtrack",
            duration=300,
            lyrics='Do re mi',
            topics='topic2,topic3',
            mp3_url='http://example.com/song2.mp3',
            cover_url='http://example.com/cover2.jpg'
        )
        self.favlist = Favlist.objects.create(
            name='User1 Favlist',
            owner=self.user1,
        )
        self.favlist.songs.set([self.song1, self.song2])

        self.client = APIClient()
        self.url = reverse('generate-songs', kwargs={'pk': self.favlist.pk})

    def test_generate_songs(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreater(len(response.data), 0)

        # Check that the generated songs have the expected attributes
        for song_data in response.data:
            self.assertEqual('SunoAI', song_data['author'])
            self.assertEqual('SunoAI Generation', song_data['album'])
