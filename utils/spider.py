import requests
from bs4 import BeautifulSoup
import time
import json
url = "https://freemusicarchive.org/genre/International/?page=2"

import requests


def find_songs(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tracks = soup.find_all('span', class_='ptxt-track')
        authors = soup.find_all('span', class_='ptxt-artist')
        albums = soup.find_all('span', class_="!hidden md:!flex ptxt-album col-span-2 truncate text-ellipsis overflow-hidden pr-8")
        durations = soup.find_all('span', class_='inline-flex items-center col-span-1 align-self-end pl-6')
        assert len(tracks)==len(authors)
    except requests.exceptions.HTTPError as e:
        return []
    
    songs = []
    for i, track in enumerate(tracks):
        title = track.find('a').text.strip()
        link = track.find('a')['href']
        author = authors[i].find('a').text.strip()
        album = albums[i].find('a').text.strip()
        duration = durations[i].text.strip()
        url = link
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser') 
        divs = soup.find_all('div', class_='w-full h-80')
        topics_a = soup.find_all('a', class_='py-1 px-2 rounded border border-blue bg-transparent text-blue font-[500] transition-all ease-in-out duration-75 text-sm hover:bg-blue hover:text-white')
        topics = []
        for topic in topics_a:
            topics.append(topic.text.strip())
        topics = ", ".join(topics)
        div = divs[0]
        img_tag = div.find('img') 
        if img_tag: 
            img_url = img_tag['src'] 
        download_links = soup.find_all('a', class_='inline-flex justify-center items-center js-download w-4 transition-colors ease-in-out duration-75 hover:text-blue')
        link=download_links[0]
        data_url = link.get('data-url') 
        print("!!!",data_url)
        if data_url: 
            response = requests.get(data_url) 
            response.raise_for_status()
            soup_temp = BeautifulSoup(response.text, 'html.parser')
            download_links = soup_temp.find_all('a', class_='download')
            link =download_links[0]
            href = link.get('href')
            print("???",href)
            # 发送GET请求，允许重定向 
            cookies = {
                "XSRF-TOKEN":"eyJpdiI6IkIrU004SjlBQjk5ZlhMNEtGSGh4TWc9PSIsInZhbHVlIjoiTzBwZVlmV1QwZmVobE9xNjducHd4V1NJTGNkVTZXWTh6eWZ2ZHRVRFRxemswRE9xN0tTNzZIbU0zY2doQ1RNSHA2NGpUT0RjVTdTYmI4dHk4RVlQZTRqZ0hVaU1Scnhtb05nS2t0TktuMXJ5Nms1M3dYY0xPSVRzQ1FmcVVvN0IiLCJtYWMiOiI3NzFlZGMwYjg4ZTkzZmU4ODQ4MWQ5MDYwY2ZlYjU3ZDI3ZWU5YzkwYjBiY2NhMWVjNzIyN2UyZDVjN2JlODM3In0%3D",
                "expires":"Wed, 18-Dec-2024 23:43:12 GMT",
                "Max-Age":"1209600",
                "path":"/",
                "samesite":"lax",
                "free_music_archive_session":"eyJpdiI6IkZBWk9QMVhEbmsyU3RxSVc4Z2NkS0E9PSIsInZhbHVlIjoiTE1UdXVhNTZ0ZzM4TVM2bWZIMTJOV056MnZBSWxvUktZR2R3NFRSUWpzOFVSVlNSNzk0bVVJOEtNek9iUmdlNnVZN0N6M3N0Sk1LRFlqdjdZV3JxaHBqdndqV3AweENUOVlHMkRMdDJxTEpNYXJjS3lrZnZoSzcvSVY3WHR4ZEMiLCJtYWMiOiJkMzU4YTgxZTlkMDJhZTY1ODFhMWU0NDRmMjcxODRkZDFlNjIwNGMwYTA1NzQwYjVkN2UwNDEwYjU1MzYwNjExIn0%3D"
            }
            response = requests.get(href, cookies=cookies, allow_redirects=True) # 获取最终重定向后的URL 
            final_url = response.url # 再次发送GET请求以获取最终的包 
            # final_response = requests.get(final_url)
            print(response)
            print(final_url)
            # print(final_response.content)
        songs.append({f'name': title, 'author': author, 'album':album, 'duration': duration, "lyrics": "", 'topics': topics, 'mp3_url':final_url, 'cover_url':img_url, })

    # print("!!!songs[0] ",songs[0])
    return songs

if __name__=='__main__':
    urls = [
        # "https://freemusicarchive.org/genre/International",
        # "https://freemusicarchive.org/genre/Blues/",
        # "https://freemusicarchive.org/genre/Jazz/",
        # "https://freemusicarchive.org/genre/novelty/",
        "https://freemusicarchive.org/genre/Old-Time__Historic/"
    ]
    for url in urls:
        for i in range(1,2):
            # if i==1:
            #     url = url
            #     songs = []
            # else:
            #     url = f"{url}?page={i}"
            url = f"{url}?pageSize=100&page=1"
            with open('./utils/songs.json', 'r', encoding='utf-8') as file: 
                songs = json.load(file)
            songs = songs + find_songs(url)
            print(songs[i*20])
            with open('./utils/songs.json', 'w', encoding='utf-8') as f: 
                json.dump(songs, f, ensure_ascii=False, indent=4)
            if len(songs) > 200:
                print("spider finish!!!")