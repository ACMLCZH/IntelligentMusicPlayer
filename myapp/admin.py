from django.contrib import admin
# Register your models here.
 
# from .models import Songs
# admin.site.register(Songs)

from .models import Song
from .documents import SongDocument
from django_elasticsearch_dsl.registries import registry
from elastic_search.methods import *
import requests
import aiohttp

class SongAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'album',
        'duration',
        'lyrics',
        'topics',
        'mp3_url',
        'cover_url',)
    search_fields = ('id', 'name', 'author')

    # def get_search_results(self, request, queryset, search_term):
    #     if search_term:
    #         search = SongDocument.search().query("multi_match", query=search_term, fields=self.search_fields)
    #         song_ids = [hit.meta.id for hit in search]
    #         queryset = queryset.filter(id__in=song_ids)
    #     return super().get_search_results(request, queryset, search_term)
    
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            # hits_total, hits = search_music(search_term, 'all', 0, 10)
            # song_ids = [hit['_source']["id"] for hit in hits]

            url = f"http://localhost:8000/song/search/?search={search_term}&limit=20" 
            response = requests.get(url) 
            if response.status_code == 200: 
                data = response.json()
            song_ids = [int(item['id']) for item in data['results']]
            queryset = queryset.filter(id__in=song_ids)
        return super().get_search_results(request, queryset, search_term)
    
    async def save_model(self, request, song, form, change): 
        add_music(song)
        data = dict(
            id=song.id,
            name=song.name,
            author=song.author,
            album=song.album,
            duration=song.duration,
            lyrics=song.lyrics,
            topics=song.topics,
            mp3_url=song.mp3_url,
            cover_url=song.cover_url,
        )
        print("Sending data: ", data)
        local_url = "http://localhost:8000/song/"
        headers = {
            'content-type': 'application/json',
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(local_url, headers=headers, json=data) as response:
                return await response.text()
        super().save_model(request, obj, form, change) 

    # session_id = request.COOKIES.get('sessionid') 
    # headers = {"Cookie": f"csrftoken={request.COOKIES.get('csrftoken')}; sessionid={session_id}" }
    def delete_queryset(self, request, queryset): 
        print("!!!",request)
        user = request.user 
        print(dir(request.user))
        if user.is_authenticated: 
            for obj in queryset: 
                print("music_obj:",obj.id)
                url = f"http://localhost:8000/song/{obj.id}/" 
                # cookies = { 'csrftoken': str(request.COOKIES.get('csrftoken')), 'sessionid': str(request.COOKIES.get('sessionid')) }
                response = requests.delete(url, )
                print("response:",response)
                return response
        super().delete_model(request, obj)
admin.site.register(Song, SongAdmin)

