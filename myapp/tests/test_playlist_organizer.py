from django.test import TestCase
import asyncio
from unittest.mock import patch, MagicMock
from music_ai.tools import PlaylistOrganizer

class PlaylistOrganizerTest(TestCase):
    def setUp(self):
        self.sample_queue = [
            {'id': 1, 'title': 'How Sweet', 'artist': 'NewJeans', 'cover': 'https://archive.org/download/How-Sweet-by-newjeans/How%20Sweet%20cover%20art.jpg', 'url': 'https://archive.org/download/How-Sweet-by-newjeans/01.%20How%20Sweet.mp3'}, 
            {'id': 2, 'title': 'OMG', 'artist': 'NewJeans', 'cover': 'https://archive.org/download/newjeans-omg-1st-single-album/cover.jpg', 'url': 'https://archive.org/download/newjeans-omg-1st-single-album/01.%20OMG.mp3'},
            {'id': 3, 'title': 'Supernatural', 'artist': 'NewJeans', 'cover': 'https://archive.org/download/02.-right-now/cover.jpg', 'url': 'https://archive.org/download/02.-right-now/01.%20Supernatural.mp3'}
        ]
        self.organizer = PlaylistOrganizer(self.sample_queue)

    def test_init(self):
        """Test PlaylistOrganizer initialization"""
        self.assertEqual(self.organizer.playlists, self.sample_queue)
        self.assertTrue(hasattr(self.organizer, 'system_prompt'))

    @patch('requests.get')
    def test_search_songs_by_name(self, mock_get):
        """Test searching songs by name"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            'id': 4,
            'name': 'Test Song',
            'author': 'Test Artist',
            'cover_url': 'http://example.com/cover.jpg',
            'mp3_url': 'http://example.com/song.mp3'
        }]
        mock_get.return_value = mock_response

        async def run_test():
            result = await self.organizer.search_songs_by_name("Test Song")
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['title'], 'Test Song')

        asyncio.run(run_test())

    @patch('requests.get')
    def test_search_songs_by_genre(self, mock_get):
        """Test searching songs by genre"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            'id': 4,
            'name': 'Pop Song',
            'author': 'Pop Artist',
            'cover_url': 'http://example.com/cover.jpg',
            'mp3_url': 'http://example.com/song.mp3'
        }]
        mock_get.return_value = mock_response

        async def run_test():
            result = await self.organizer.search_songs_by_genre("pop")
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['title'], 'Pop Song')

        asyncio.run(run_test())

    def test_parse_instruction(self):
        """Test parsing different types of instructions"""
        test_cases = [
            {
                'instruction': 'Add Shooting Star at the end',
                'expected': {'type': 'add', 'song_name': 'Shooting Star', 'position': 3}
            },
            {
                'instruction': 'shuffle the playlist',
                'expected': {
                'type': 'other',
                'song_ids': lambda ids: (
                    set(ids) == {1, 2, 3} and
                    ids != [1, 2, 3]           
                ) # Same ids but in different order
            }
            },
            {
                'instruction': 'remove OMG from the playlist',
                'expected': {'type': 'remove', 'song_name': 'OMG'}
            },
            {
                'instruction': 'play How Sweet every 2 songs',
                'expected': {'type': 'pattern', 'song_name': 'How Sweet', 'interval': 2}
            }
        ]

        async def run_test():
            for test in test_cases:
                result = await self.organizer.parse_instruction(test['instruction'])
                self.assertEqual(result['type'], test['expected']['type'])
                if result['type'] == 'add':
                    self.assertEqual(result['song_name'], test['expected']['song_name'])
                    self.assertEqual(result['position'], test['expected']['position'])
                elif result['type'] == 'other':
                    self.assertTrue(test['expected']['song_ids'](result['song_ids']))
                elif result['type'] == 'remove':
                    self.assertEqual(result['song_name'], test['expected']['song_name'])
                elif result['type'] == 'pattern':
                    self.assertEqual(result['song_name'], test['expected']['song_name'])
                    self.assertEqual(result['interval'], test['expected']['interval'])

        asyncio.run(run_test())

    def test_reorganize_playlist(self):
        """Test full playlist reorganization"""
        async def run_test():
            # Test adding a song
            result = await self.organizer.reorganize_playlist("Add a song OMG at the beginning")
            self.assertGreater(len(result), 0)

            # Test shuffling
            result = await self.organizer.reorganize_playlist("shuffle the playlist")
            self.assertEqual(len(result), len(self.sample_queue))

        asyncio.run(run_test())

    def test_ids_to_playlist(self):
        """Test converting IDs back to playlist items"""
        ids = [2, 1, 3]
        result = self.organizer._ids_to_playlist(ids)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['id'], 2)
        self.assertEqual(result[1]['id'], 1)
        self.assertEqual(result[2]['id'], 3)