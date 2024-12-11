import os
from django.conf import settings
from django_elasticsearch_dsl import Document, Index
from django_elasticsearch_dsl.registries import registry
from .models import Song

IS_TESTING = getattr(settings, "TESTING", False)

index_name = "song"
if IS_TESTING:
    index_name = "test_song"  # Use a separate test index


@registry.register_document
class SongDocument(Document):
    class Index:
        name = index_name  # Use the conditional index name
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Song
        fields = [
            "id",
            "name",
            "author",
            "album",
            "duration",
            "lyrics",
            "topics",
            "mp3_url",
            "cover_url",
        ]
