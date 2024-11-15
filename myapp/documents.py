from django_elasticsearch_dsl import Document, fields 
from django_elasticsearch_dsl.registries import registry 
from .models import Songs 

@registry.register_document 
class SongDocument(Document): 
    class Index: 
        name = 'songs' 
        settings = { 'number_of_shards': 1, 'number_of_replicas': 0 } 
    class Django: 
        model = Songs 
        fields =  ['id', 'name', 'author','duration','lyrics',  'url']