import requests
import json
from typing import List, Dict
from .ai_clients import suno_client, openai_client
import time

local_song_url = "http://localhost:8000/song/"
local_favlist_url = "http://localhost:8000/favlist/"
callback_url = "https://webhook.site/"
local_headers = {
    'content-type': 'application/json',
}
suno_artist = 'SunoAI'
suno_album = 'SunoAI Generation'
default_response = {
    "success": True,
    "data": [{
        "state": "succeeded",
        "id": "fabfea10-4805-4b81-b54d-ee089ae1533a_1",
        "title": "The Rhyme Chronicles",
        "image_url": "https://cdn2.suno.ai/image_ee0717ad-aded-4008-a30c-4f43bbcb3fc3.jpeg",
        "lyric": "[Verse 1]\nGot the city lights flickerin\", a masterpiece in bricks,\nSippin\" on wisdom, every corner tales stick.\nDodgin\" pitfalls, my Nike kicks on a mission,\nSlingin’ poetry, listen close, no intermission.\n\n[Verse 2]\nAlleyways been my stage, where I earn my crown,\nGraffiti dreams speak loud, never backin\" down.\nSurvival tactics, every street got a code,\nIn this jungle, respect paid in heavy loads.\n\n[Chorus]\nRhymes sharp as a blade, cut through the night,\nStories etched in shadows, truth in the fight.\nCiphers in the park, life’s gritty aesthetic,\nSpittin’ for the love, ink eternally kinetic.\n\n[Verse 3]\nEchoes in the hallways, memories in the dust,\nChasin’ after glory while dodgin’ the rust.\nMelodies in the sirens, beats in the grind,\nClock ticks relentless, but I’m never behind.\n\n[Bridge]\nLocked eyes with the storm, composed in the chaos,\nKeys to the rhythm, my heart syncopated dauntless.\nPages of the struggle, tales of the street,\nEvery bar scars deep, but victory’s sweet.\n\n[Verse 4]\nBlueprints on my mind, legacy in the flows,\nResilience in the veins, path in prose.\nVerse painted visceral, truths carved in stone,\nEvery neighborhood a chapter, every verse a throne.",
        "audio_url": "https://cdn1.suno.ai/ee0717ad-aded-4008-a30c-4f43bbcb3fc3.mp3",
        "video_url": "https://cdn1.suno.ai/ee0717ad-aded-4008-a30c-4f43bbcb3fc3.mp4",
        "created_at": "2024-11-27T06:22:19.697Z",
        "model": "chirp-v3-5",
        "prompt": "Make a song of rap and hip-hop music, with a preference for hard-hitting beats, complex lyricism, and storytelling, from both classic and contemporary artists.",
        "style": "High quality",
        "duration": 189
    }, {
        "state": "succeeded",
        "id": "fabfea10-4805-4b81-b54d-ee089ae1533a_2",
        "title": "The Rhyme Chronicles",
        "image_url": "https://cdn2.suno.ai/image_7d47a123-b4e0-436d-8b01-6e9acbc5f1bf.jpeg",
        "lyric": "[Verse 1]\nGot the city lights flickerin\", a masterpiece in bricks,\nSippin\" on wisdom, every corner tales stick.\nDodgin\" pitfalls, my Nike kicks on a mission,\nSlingin’ poetry, listen close, no intermission.\n\n[Verse 2]\nAlleyways been my stage, where I earn my crown,\nGraffiti dreams speak loud, never backin\" down.\nSurvival tactics, every street got a code,\nIn this jungle, respect paid in heavy loads.\n\n[Chorus]\nRhymes sharp as a blade, cut through the night,\nStories etched in shadows, truth in the fight.\nCiphers in the park, life’s gritty aesthetic,\nSpittin’ for the love, ink eternally kinetic.\n\n[Verse 3]\nEchoes in the hallways, memories in the dust,\nChasin’ after glory while dodgin’ the rust.\nMelodies in the sirens, beats in the grind,\nClock ticks relentless, but I’m never behind.\n\n[Bridge]\nLocked eyes with the storm, composed in the chaos,\nKeys to the rhythm, my heart syncopated dauntless.\nPages of the struggle, tales of the street,\nEvery bar scars deep, but victory’s sweet.\n\n[Verse 4]\nBlueprints on my mind, legacy in the flows,\nResilience in the veins, path in prose.\nVerse painted visceral, truths carved in stone,\nEvery neighborhood a chapter, every verse a throne.",
        "audio_url": "https://cdn1.suno.ai/7d47a123-b4e0-436d-8b01-6e9acbc5f1bf.mp3",
        "video_url": "https://cdn1.suno.ai/7d47a123-b4e0-436d-8b01-6e9acbc5f1bf.mp4",
        "created_at": "2024-11-27T06:22:19.716Z",
        "model": "chirp-v3-5",
        "prompt": "Make a song of rap and hip-hop music, with a preference for hard-hitting beats, complex lyricism, and storytelling, from both classic and contemporary artists.",
        "style": "High quality",
        "duration": 97
    }],
    "task_id": "7a1dceb4-aeae-46b6-b86b-49a8930d2f40"
}

generate_system_prompt = \
    "You are an expert music analyst. Your task is to evaluate a list of songs provided by the user "\
    "and summarize the music styles and properties that the user probably enjoys."

def generate_songs(songs_jsons: List[Dict]) -> List[Dict]:
    songs_info = "\n".join([
        f"Title: {song_json['name']}, Artist: {song_json['author']}, Album: {song_json['album']}"
        for song_json in songs_jsons
    ])

    generate_user_prompt = \
        "Here is a list of songs:\n"\
        f"{songs_info}\n"\
        "Based on these songs, summarize the music styles and properties that the user likely enjoys in one sentence. "\
        "Your answer should be recapitulatory and begin with \"The user likely enjoys...\"."
    print(generate_user_prompt)

    generate_data = {
        "model": "gpt-4",
        "messages": [{
            "role": "system",
            "content": generate_system_prompt
        }, {
            "role": "user",
            "content": generate_user_prompt
        }],
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 1,
    }
    generate_answer = openai_client.request(generate_data)
    while not generate_answer.startswith("The user likely enjoys") or len(generate_answer) > 200:
        print(f"Warning: the answer '{generate_answer}' does not meet the requirement, re-generate now.")
        generate_answer = openai_client.request(generate_data)
    print(generate_answer)

    suno_prompt = "Make a song of " + generate_answer[23:]
    suno_data = {
        'action': 'generate',
        'prompt': suno_prompt,
        'model': 'chirp-v3-5',
        'custom': False,
        'instrumental': False,
    }
    try:
        # raise requests.exceptions.RequestException
        suno_response = suno_client.request(suno_data)
    except requests.exceptions.RequestException as e:
        suno_response = default_response
    except:
        raise

    # while True:
    #     time.sleep(60)
    #     response = requests.get(f"{callback_url}/{task_id}", headers=local_headers)
    #     if response.status_code == 200:
    #         suno_response = response.json()
    #         break
    #     else:
    #         print(response.text)

    music_jsons = suno_response['data']
    print(music_jsons)
    music_list = list()
    for music_json in music_jsons:
        local_data = {
            'name': music_json['title'],
            'author': suno_artist,
            'album': suno_album,
            'duration': music_json['duration'],
            'lyrics': music_json['lyric'],
            'topics': "AI generated",
            'mp3_url': music_json['audio_url'],
            'cover_url': music_json['image_url'],
        }
        local_response = requests.post(local_song_url, headers=local_headers, json=local_data)
        if local_response.status_code >= 300:
            raise Exception(f"Failed to post song to local server with error: {local_response.status_code}, {local_response.text}.")
        else:
            music_list.append(local_response.json())

    return music_list


class PlaylistOrganizer:
    def __init__(self):
        self.playlists = []
        self.system_prompt = \
            "You are a music playlist organizer. Parse the user's instruction into a structured format."\
            "Return a JSON object with:"\
            "- type: \"pattern\" or \"genre\""\
            "- song_name: (if pattern type)"\
            "- interval: (if pattern type, integer) "\
            "- genre: (if genre type)"
        
    async def search_songs_by_name(self, name: str) -> List[Dict]:
        # Stub - will be replaced with actual API call
        # TODO: Use aiohttp
        local_response = requests.get(
            local_favlist_url.format(search=name, field='name'),
            headers=local_headers
        )
        print([song for song in self.playlists if song['title'].lower() == name.lower()])
        print(local_response.json())
        
        retrieved_song = local_response.json()
        return [{
            'id': song['id'],
            'title': song['name'],
            'artist': song['author'],
            'cover': song['cover_url'],
            'url': song['mp3_url']
        } for song in retrieved_song]
    
    async def search_songs_by_genre(self, genre: str) -> List[Dict]:
        # Stub - will be replaced with actual API call 
        # TODO: Use aiohttp
        local_response = requests.get(
            local_favlist_url.format(search=genre, field='topics'),
            headers=local_headers
        )
        retrieved_song = local_response.json()
        return [{
            'id': song['id'],
            'title': song['name'],
            'artist': song['author'],
            'cover': song['cover_url'],
            'url': song['mp3_url']
        } for song in retrieved_song]

    async def parse_instruction(self, instruction: str) -> Dict:
        """Use GPT to parse the natural language instruction"""
        # Convert string response to Dict
        organize_data = {
            "model": "gpt-4o-mini",
            "messages": [{
                "role": "system",
                "content": self.system_prompt
            }, {
                "role": "user",
                "content": instruction
            }],
        }
        content = openai_client.request(organize_data)
        return json.loads(content)

    async def reorganize_playlist(self, instruction: str) -> List[Dict]:
        """Main method to reorganize playlist based on instruction"""
        print(f"Received instruction: {instruction}")
        parsed = await self.parse_instruction(instruction)
        print(f"Parsed instruction: {parsed}")
        
        if parsed['type'] == 'pattern':
            print(f"Pattern-based reorganization: {parsed['song_name']} every {parsed['interval']} songs")
            # Handle pattern-based organization (e.g. "OMG every 2 songs")
            song = await self.search_songs_by_name(parsed['song_name'])
            if not song:
                raise ValueError(f"Song {parsed['song_name']} not found")
                
            interval = int(parsed['interval'])
            new_playlist = []
            other_songs = [s for s in self.playlists if s['title'] != song[0]['title']]
            
            # Insert requested song at every interval position
            j = 0  # Counter for other songs
            for i in range(len(self.playlists) + len(self.playlists) // interval):  # Extended length
                if i % (interval + 1) == 0:  # +1 because we want song after every N songs
                    new_playlist.append(song[0])
                else:
                    if j < len(other_songs):
                        new_playlist.append(other_songs[j])
                        j += 1
                        
        print(f"New playlist: {[s['title'] for s in new_playlist]}")
        return new_playlist


if __name__ == "__main__":
    mp3_url = "https://cdn1.suno.ai/d4bd4d4e-1123-4d8f-998e-0e08cec2e808.mp3"
    cover_url = "https://cdn2.suno.ai/image_d4bd4d4e-1123-4d8f-998e-0e08cec2e808.jpeg"