from django.contrib import admin

# Register your models here.

# from .models import Songs
# admin.site.register(Songs)
from django.contrib import messages
from .models import Song
from .documents import SongDocument
from django_elasticsearch_dsl.registries import registry
import requests
import aiohttp
from rest_framework.authtoken.models import Token
from django.conf import settings


class SongAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "author",
        "album",
        "duration",
        "lyrics",
        "topics",
        "mp3_url",
        "cover_url",
    )
    search_fields = ("id", "name", "author")

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            url = f"http://localhost:8000/song/search/?search={search_term}&ai=True"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
            song_ids = [int(item["id"]) for item in data]
            queryset = queryset.filter(id__in=song_ids)
        return super().get_search_results(request, queryset, "")

    def save_model(self, request, song, form, change):
        sessionid = request.COOKIES.get("sessionid")
        csrftoken = request.COOKIES.get("csrftoken")

        if not sessionid or not csrftoken:
            return

        cookies = {"sessionid": sessionid, "csrftoken": csrftoken}
        headers = {"X-CSRFToken": csrftoken}
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
        if not change:
            response = requests.post(
                url="http://localhost:8000/song/",
                json=data,
                cookies=cookies,
                headers=headers,
            )
        else:
            response = requests.put(
                url=f"http://localhost:8000/song/{song.id}/",
                json=data,
                cookies=cookies,
                headers=headers,
            )

    def delete_queryset(self, request, queryset):
        # Extract session ID and CSRF token from the request cookies
        sessionid = request.COOKIES.get("sessionid")
        csrftoken = request.COOKIES.get("csrftoken")

        if not sessionid or not csrftoken:
            return None

        cookies = {"sessionid": sessionid, "csrftoken": csrftoken}
        headers = {"X-CSRFToken": csrftoken}

        for obj in queryset:
            del_id = obj.id
            url = f"http://localhost:8000/song/{del_id}/"
            response = requests.delete(url, cookies=cookies, headers=headers)


admin.site.register(Song, SongAdmin)
