from django.contrib import admin
# Register your models here.
 
# from .models import Songs
# admin.site.register(Songs)

from .models import Song
from .documents import SongDocument
from django_elasticsearch_dsl.registries import registry
from elastic_search.methods import *

class SongAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'duration', 'lyrics', 'mp3_url', 'cover_url')
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
            hits_total, hits = search_music(search_term, 'all', 0, 10)
            song_ids = [int(hit['_source']['id']) for hit in hits]
            queryset = queryset.filter(id__in=song_ids)
        return super().get_search_results(request, queryset, search_term)

    def save_model(self, request, obj, form, change): 
        super().save_model(request, obj, form, change) 
        add_music(obj)

    def delete_queryset(self, request, queryset): 
        for obj in queryset: 
            delete_music(obj)
        super().delete_model(request, obj)
admin.site.register(Song, SongAdmin)

