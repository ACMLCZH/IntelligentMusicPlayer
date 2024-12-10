# myapp/models.py

from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Song(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    duration = models.IntegerField()
    lyrics = models.CharField(max_length=5000)
    topics = models.CharField(max_length=500)
    mp3_url = models.CharField(max_length=500)
    cover_url = models.CharField(max_length=500)

    def __str__(self):
        return self.name
    # class Meta:
    #     verbose_name = 'Song'
    #     verbose_name_plural = verbose_name

class Favlist(models.Model):
    name = models.CharField(max_length=100)
    songs = models.ManyToManyField(Song, related_name='favlists')
    owner = models.ForeignKey(User, related_name='favlists', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserFav(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='user_favs'
    )
    favlists = models.ManyToManyField(Favlist, related_name='user_favs')

    def __str__(self):
        return f"{self.user.username}'s Favorites"