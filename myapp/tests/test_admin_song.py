from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from ..models import Song
from ..admin import SongAdmin

class SongAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()
        self.song_admin = SongAdmin(Song, self.admin_site)
        self.user = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')

    @patch('requests.get')
    def test_get_search_results(self, mock_get):
        request = self.factory.get('/admin/app/song/')
        request.user = self.user
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'id': 1}, {'id': 2}]
        mock_get.return_value = mock_response

        song1 = Song(id=1, name='Test', author='Test Author', album='Test Album', duration='220', lyrics='Test Lyrics', topics='Test Topics', mp3_url='http://example.com/test.mp3', cover_url='http://example.com/test.jpg')
        self.song_admin.save_model(request, song1, None, change=False)
        song2 = Song(id=2, name='Test2', author='Test Author1', album='Test Album', duration='220', lyrics='Test Lyrics', topics='Test Topics', mp3_url='http://example.com/test.mp3', cover_url='http://example.com/test.jpg')
        self.song_admin.save_model(request, song2, None, change=False)
        song1.save() 
        song2.save() 
        queryset = Song.objects.all()
        search_term = 'Test'
        results = self.song_admin.get_search_results(request, queryset, search_term)
        self.assertEqual(results[0].count(), 2)

    @patch('requests.post')
    @patch('requests.put')
    def test_save_model(self, mock_put, mock_post):
        request = self.factory.post('/admin/app/song/')
        request.user = self.user
        request.COOKIES['sessionid'] = 'fake-sessionid'
        request.COOKIES['csrftoken'] = 'fake-csrftoken'

        song = Song(id=1, name='Test1', author='Test Author', album='Test Album', duration='220', lyrics='Test Lyrics', topics='Test Topics', mp3_url='http://example.com/test.mp3', cover_url='http://example.com/test.jpg')

        # Test creating a new song
        self.song_admin.save_model(request, song, None, change=False)
        mock_post.assert_called_once()

        # Test updating an existing song
        self.song_admin.save_model(request, song, None, change=True)
        mock_put.assert_called_once()

    @patch('requests.delete')
    def test_delete_queryset(self, mock_delete):
        request = self.factory.post('/admin/app/song/')
        request.user = self.user
        request.COOKIES['sessionid'] = 'fake-sessionid'
        request.COOKIES['csrftoken'] = 'fake-csrftoken'

        song1 = Song.objects.create(name='Test Song 1', author='Test Author', album='Test Album', duration='220', lyrics='Test Lyrics', topics='Test Topics', mp3_url='http://example.com/test1.mp3', cover_url='http://example.com/test1.jpg')
        song2 = Song.objects.create(name='Test Song 2', author='Test Author', album='Test Album', duration='220', lyrics='Test Lyrics', topics='Test Topics', mp3_url='http://example.com/test2.mp3', cover_url='http://example.com/test2.jpg')

        queryset = Song.objects.filter(id__in=[song1.id, song2.id])
        self.song_admin.delete_queryset(request, queryset)
        self.assertEqual(mock_delete.call_count, 2)

        # Test case when sessionid or csrftoken is missing 
        request.COOKIES.pop('sessionid') 
        result = self.song_admin.delete_queryset(request, queryset) 
        self.assertIsNone(result) 
        self.assertEqual(mock_delete.call_count, 2)

        # Reset cookies for the next test case
        request.COOKIES['sessionid'] = 'fake-sessionid'

        # Test case when both sessionid and csrftoken are present
        result = self.song_admin.delete_queryset(request, queryset)
        self.assertIsNone(result)
        self.assertEqual(mock_delete.call_count, 4)

        # Test case when delete request fails
        mock_delete.return_value.status_code = 400
        result = self.song_admin.delete_queryset(request, queryset)
        self.assertIsNone(result)
        self.assertEqual(mock_delete.call_count, 6)  # 2 more calls from this test case
    
# from unittest.mock import patch, MagicMock

# @patch('requests.delete')
# def test_delete_queryset(self, mock_delete):
#     request = self.factory.post('/admin/app/song/')
#     request.user = self.user
#     request.COOKIES['sessionid'] = 'fake-sessionid'
#     request.COOKIES['csrftoken'] = 'fake-csrftoken'

#     song1 = Song.objects.create(name='Test Song 1', author='Test Author', album='Test Album', duration='220', lyrics='Test Lyrics', topics='Test Topics', mp3_url='http://example.com/test1.mp3', cover_url='http://example.com/test1.jpg')
#     song2 = Song.objects.create(name='Test Song 2', author='Test Author', album='Test Album', duration='220', lyrics='Test Lyrics', topics='Test Topics', mp3_url='http://example.com/test2.mp3', cover_url='http://example.com/test2.jpg')

#     queryset = Song.objects.filter(id__in=[song1.id, song2.id])

#     # Test case when sessionid or csrftoken is missing
#     request.COOKIES.pop('sessionid')
#     result = self.song_admin.delete_queryset(request, queryset)
#     self.assertIsNone(result)
#     self.assertEqual(mock_delete.call_count, 0)

    
