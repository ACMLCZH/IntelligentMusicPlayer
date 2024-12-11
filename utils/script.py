import json
import asyncio
import aiohttp

CONCURRENT_LIMIT = 8
semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)


async def convert_duration_to_minutes(duration_str):
    minutes, seconds = map(int, duration_str.split(":"))
    total_minutes = minutes * 60 + seconds
    return int(total_minutes)


async def send_song_data(song, session, auth):
    async with semaphore:
        name, author, album, duration, lyrics, topics, mp3_url, cover_url = (
            song.values()
        )
        duration = await convert_duration_to_minutes(duration)
        data = {
            "name": name,
            "author": author,
            "album": album,
            "duration": duration,
            "lyrics": ".",
            "topics": topics,
            "mp3_url": mp3_url,
            "cover_url": cover_url,
        }
        print("Sending data: ", data)
        local_url = "http://localhost:8000/song/"
        headers = {
            "content-type": "application/json",
        }
        async with session.post(
            local_url, headers=headers, json=data, auth=auth
        ) as response:
            return await response.text()


async def main():
    username = input("Enter username: ")
    password = input("Enter password: ")

    auth = aiohttp.BasicAuth(username, password)

    with open("utils/songs.json", "r", encoding="utf-8") as f:
        songs = json.load(f)

    async with aiohttp.ClientSession() as session:
        tasks = [send_song_data(song, session, auth) for song in songs]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            print("Response: ", response)


if __name__ == "__main__":
    asyncio.run(main())
