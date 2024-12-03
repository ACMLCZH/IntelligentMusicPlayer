from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json

driver = webdriver.Chrome()

with open('songs.json', 'r', encoding='utf-8') as f: 
    songs = json.load(f)

for song in songs:
    print("!!add song:", song)
    name, author, album, duration, lyrics, topics, mp3_url, cover_url = song
    driver.get("http://127.0.0.1:8000/admin/myapp/song/add/")
    driver.find_element(By.NAME, "name").send_keys(name)
    driver.find_element(By.NAME, "author").send_keys(author)
    driver.find_element(By.NAME, "album").send_keys(album)
    driver.find_element(By.NAME, "duration").send_keys(duration)
    driver.find_element(By.NAME, "lyrics").send_keys(lyrics)
    driver.find_element(By.NAME, "topics").send_keys(topics)
    driver.find_element(By.NAME, "mp3_url").send_keys(mp3_url)
    driver.find_element(By.NAME, "cover_url").send_keys(cover_url)
    driver.find_element(By.NAME, "_save").click()

driver.quit()
