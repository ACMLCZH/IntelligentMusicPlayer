import requests

# api at: https://api.topmediai.com/docs#/AI-Music-Generator/
api_key = '209beb49029b4214bf45c2ce2759607a'
api_key = 'bb7ac057b0724b15a6b7ecb96d9401a3'
artist = 'topmediai'
lyric_url = "https://api.topmediai.com/v1/lyrics"
music_url = "https://api.topmediai.com/v1/music"
headers = {
    'accept': 'application/json',
    'x-api-key': api_key,
    'Content-Type': 'application/json',
}

def generate_song(prompt):
    lyric_data = {
        'prompt': prompt,
    }
    lyric_response = requests.post(lyric_url, headers=headers, json=lyric_data)
    if lyric_response.status_code != 200:
        raise Exception(f'Error: {lyric_response.status_code}, {lyric_response.text}')

    lyric_json = lyric_response.json()['data']
    lyric = lyric_json['text']
    title = lyric_json['title']
    print('Lyrics generated successfully: ', lyric)

    music_data = {
        "is_auto": 1,
        'prompt': prompt,
        "lyrics": lyric,
        "title": title,
    }
    music_response = requests.post(music_url, headers=headers, json=music_data)
    if music_response.status_code != 200:
        raise Exception(f'Error: {music_response.status_code}, {music_response.text}')
    print('Music generated successfully!')

if __name__ == "__main__":
    # Play the first song in memory
    audio_data = generate_song("Make a song of rap and hip-hop music, with a preference for hard-hitting beats, complex lyricism, and storytelling, from both classic and contemporary artists.")
