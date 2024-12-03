from django.contrib import admin
# Register your models here.
 
# from .models import Songs
# admin.site.register(Songs)

from .models import Song
from .documents import SongDocument
from django_elasticsearch_dsl.registries import registry
from elastic_search.methods import *
from music_ai.gpt4 import make_song_prompt

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
            # print("!!!!!!",search_term)
            # clear_es_database()
            hits_total, hits = search_music(search_term, 'all', 0, 10)
            for hit in hits:
                print(hit)
            song_names = [hit['_source']["name"] for hit in hits]
            queryset = queryset.filter(name__in=song_names)
        return super().get_search_results(request, queryset, search_term)
    
    def save_model(self, request, obj, form, change): 
        super().save_model(request, obj, form, change) 
        add_music(obj)

    def delete_queryset(self, request, queryset): 
        for obj in queryset: 
            delete_music(obj)
        super().delete_model(request, obj)
admin.site.register(Song, SongAdmin)

