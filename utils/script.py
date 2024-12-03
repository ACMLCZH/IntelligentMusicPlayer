from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json
import time
import requests

# driver = webdriver.Edge()

with open('songs.json', 'r', encoding='utf-8') as f: 
    songs = json.load(f)

def convert_duration_to_minutes(duration_str): 
    # print("duration_str",duration_str)
    # 分割字符串，获取分钟和秒 
    minutes, seconds = map(int, duration_str.split(':')) 
    # 将分钟和秒转换为总分钟数 
    total_minutes = minutes*60 + seconds
    return int(total_minutes)

for song in songs:
    # print("!!add song:", song)
    name, author, album, duration, lyrics, topics, mp3_url, cover_url = song.values()
    # print("!!!",duration)
    duration = convert_duration_to_minutes(duration)
    data = {
        "name": name,
        "author": author,
        "album": album,
        "duration": duration,
        "lyrics": '.',
        "topics": ', '.join(topics),
        "mp3_url": mp3_url,
        "cover_url": cover_url,
    }
    print("data: ",data)
    local_url = "http://localhost:8000/song/"
    local_headers = {
        'content-type': 'application/json',
    }
    local_response = requests.post(local_url, headers=local_headers, json=data)
    