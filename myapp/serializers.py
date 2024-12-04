# myapp/serializers.py

from rest_framework import serializers
from .models import Song, Favlist, UserFav
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .documents import SongDocument

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

class SongDocumentSerializer(DocumentSerializer):
    class Meta:
        document = SongDocument
        fields = (
            'id',
            'name',
            'author',
            'album',
            'duration',
            'lyrics',
            'topics',
            'mp3_url',
            'cover_url',
        )


class FavlistSerializer(serializers.ModelSerializer):
    songs = serializers.PrimaryKeyRelatedField(queryset=Song.objects.all(), many=True)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Favlist
        fields = ['id', 'name', 'songs', 'owner']

class FavlistBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favlist
        fields = ['id', 'name', 'owner']


class UserFavSerializer(serializers.ModelSerializer):
    favlists = serializers.PrimaryKeyRelatedField(queryset=Favlist.objects.all(), many=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserFav
        fields = ['user', 'favlists']
