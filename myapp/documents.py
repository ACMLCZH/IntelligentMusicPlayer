from django_elasticsearch_dsl import Document, Index
from django_elasticsearch_dsl.registries import registry 
from .models import Song 

@registry.register_document 
class SongDocument(Document): 
    class Index: 
        name = 'song' 
        settings = { 'number_of_shards': 1, 'number_of_replicas': 0 } 
    class Django: 
        model = Song 
        fields =  ['id', 'name', 'author', 'album', 'duration','lyrics', 'topics', 'mp3_url', 'cover_url']