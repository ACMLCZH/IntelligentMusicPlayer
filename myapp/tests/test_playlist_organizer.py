from django.test import TestCase
from music_ai.tools import PlaylistOrganizer
import asyncio
from unittest.mock import patch, MagicMock

class PlaylistOrganizerTest(TestCase):
    def setUp(self):
        self.queue = [
            {
                'id': 1, 
                'name': 'How Sweet', 
                'author': 'NewJeans', 
                'album': 'How Sweet', 
                'duration': 177, 
                'lyrics': '...', 
                'topics': 'kpop, country', 
                'mp3_url': 'https://archive.org/download/How-Sweet-by-newjeans/01.%20How%20Sweet.mp3', 
                'cover_url': 'https://archive.org/download/How-Sweet-by-newjeans/How%20Sweet%20cover%20art.jpg'
            }, 
            {
                'id': 2, 
                'name': 'OMG', 
                'author': 'NewJeans', 
                'album': 'OMG', 
                'duration': 430, 
                'lyrics': '...', 
                'topics': 'kpop, rock', 
                'mp3_url': 'https://archive.org/download/newjeans-omg-1st-single-album/01.%20OMG.mp3', 
                'cover_url': 'https://archive.org/download/newjeans-omg-1st-single-album/cover.jpg'
            }, 
            {
                'id': 3, 
                'name': 'Supernatural', 
                'author': 'NewJeans', 
                'album': 'How Sweet', 
                'duration': 123, 
                'lyrics': '...', 
                'topics': 'kpop, rnb, r&b', 
                'mp3_url': 'https://archive.org/download/02.-right-now/01.%20Supernatural.mp3', 
                'cover_url': 'https://archive.org/download/02.-right-now/cover.jpg'
            }
        ]
        self.organizer = PlaylistOrganizer(self.queue)    
    
    async def async_test(self, coroutine):
        """Helper method to run async tests"""
        return await coroutine

    def test_ids_to_playlist(self):
        """Test converting IDs back to playlist items"""
        ids = [2, 1, 3]
        result = self.organizer._ids_to_playlist(ids)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['id'], 2)
        self.assertEqual(result[1]['id'], 1)
        self.assertEqual(result[2]['id'], 3)

    @patch('requests.get')
    def test_search_songs_by_genre(self, mock_get):
        """Test genre-based song search"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 4,
                'name': 'Test Song',
                'author': 'Test Artist',
                'cover_url': 'test_cover.jpg',
                'mp3_url': 'test.mp3'
            }
        ]
        mock_get.return_value = mock_response

        result = asyncio.run(self.organizer.search_songs_by_genre('rock'))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test Song')

    @patch('music_ai.tools.PlaylistOrganizer.search_songs_by_name')
    async def test_reorganize_playlist_add(self, mock_search):
        """Test adding a song to playlist"""
        mock_search.return_value = [{
            'id': 4,
            'title': 'New Song',
            'artist': 'New Artist'
        }]
        
        instruction = "Add New Song at the end"
        result = await self.organizer.reorganize_playlist(instruction)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[-1]['title'], 'New Song')

    @patch('music_ai.tools.PlaylistOrganizer.search_songs_by_genre')
    async def test_reorganize_playlist_genre(self, mock_search):
        """Test reorganizing by genre"""
        mock_search.return_value = [
            {
                'id': 5,
                'title': 'Rock Song',
                'artist': 'Rock Artist'
            }
        ]
        
        instruction = "Add some rock songs"
        result = await self.organizer.reorganize_playlist(instruction)
        self.assertTrue(any(song['title'] == 'Rock Song' for song in result))

    async def test_parse_instruction(self):
        """Test instruction parsing"""
        test_cases = [
            {
                'instruction': 'Add Shooting Star at the end',
                'expected': {'type': 'add', 'song_name': 'Shooting Star', 'position': 3}
            },
            {
                'instruction': 'shuffle the playlist',
                'expected': {'type': 'other'}
            },
        ]

        for case in test_cases:
            result = await self.organizer.parse_instruction(case['instruction'])
            self.assertEqual(result['type'], case['expected']['type'])
            if 'song_name' in case['expected']:
                self.assertEqual(result['song_name'], case['expected']['song_name'])