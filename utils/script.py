import json
import asyncio
import aiohttp

# 定义并发限制为16
CONCURRENT_LIMIT = 16
semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

async def convert_duration_to_minutes(duration_str): 
    # 分割字符串，获取分钟和秒 
    minutes, seconds = map(int, duration_str.split(':')) 
    # 将分钟和秒转换为总秒数
    total_minutes = minutes * 60 + seconds
    return int(total_minutes)

async def send_song_data(song, session, auth):
    async with semaphore:  # 使用信号量限制并发数
        name, author, album, duration, lyrics, topics, mp3_url, cover_url = song.values()
        duration = await convert_duration_to_minutes(duration)
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
        print("Sending data: ", data)
        local_url = "http://localhost:8000/song/"
        headers = {
            'content-type': 'application/json',
        }
        async with session.post(local_url, headers=headers, json=data, auth=auth) as response:
            return await response.text()

async def main():
    username = input("Enter username: ")
    password = input("Enter password: ")

    # 创建认证信息
    auth = aiohttp.BasicAuth(username, password)

    # 读取 JSON 文件
    with open('utils/songs.json', 'r', encoding='utf-8') as f: 
        songs = json.load(f)

    async with aiohttp.ClientSession() as session:
        tasks = [send_song_data(song, session, auth) for song in songs]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            print("Response: ", response)

# 运行异步主程序
if __name__ == '__main__':
    asyncio.run(main())
