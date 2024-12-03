import requests
from bs4 import BeautifulSoup
import time
import json
url = "https://freemusicarchive.org/genre/International/?page=2"

def find_songs(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    tracks = soup.find_all('span', class_='ptxt-track')
    authors = soup.find_all('span', class_='ptxt-artist')
    albums = soup.find_all('span', class_="!hidden md:!flex ptxt-album col-span-2 truncate text-ellipsis overflow-hidden pr-8")
    durations = soup.find_all('span', class_='inline-flex items-center col-span-1 align-self-end pl-6')
    assert len(tracks)==len(authors)

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
        div = divs[0]
        img_tag = div.find('img') 
        if img_tag: 
            img_url = img_tag['src'] 
        download_links = soup.find_all('a', class_='inline-flex justify-center items-center js-download w-4 transition-colors ease-in-out duration-75 hover:text-blue')
        link=download_links[0]
        data_url = link.get('data-url') 
        if data_url: 
            response = requests.get(data_url) 
            response.raise_for_status()
            soup_temp = BeautifulSoup(response.text, 'html.parser')
            download_links = soup_temp.find_all('a', class_='download')
            link =download_links[0]
            href = link.get('href')
        songs.append({f'name': title, 'author': author, 'album':album, 'duration': duration, "lyrics": "", 'topics': topics, 'mp3_url':href, 'cover_url':img_url, })

    # print("!!!songs[0] ",songs[0])
    return songs

if __name__=='__main__':
    urls = [
        # "https://freemusicarchive.org/genre/International",
        "https://freemusicarchive.org/genre/Blues/",
        "https://freemusicarchive.org/genre/Jazz/",
        "https://freemusicarchive.org/genre/novelty/",
        "https://freemusicarchive.org/genre/Old-Time__Historic/"
    ]
    for url in urls:
        for i in range(1,100):
            if i==1:
                url = "https://freemusicarchive.org/genre/International"
                songs = []
            else:
                url = f"{url}?page={i}"
                with open('songs.json', 'r', encoding='utf-8') as file: 
                    songs = json.load(file)
            songs = songs + find_songs(url)
            with open('songs.json', 'w', encoding='utf-8') as f: 
                json.dump(songs, f, ensure_ascii=False, indent=4)
            if len(songs) > 200:
                print("spider finish!!!")