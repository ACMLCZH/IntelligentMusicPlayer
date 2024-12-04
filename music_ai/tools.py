import requests
import json
from typing import List, Dict
from .ai_clients import suno_client, openai_client

local_song_url = "http://localhost:8000/song/"
local_favlist_url = "http://localhost:8000/favlist/"
local_headers = {
    'content-type': 'application/json',
}
suno_artist = 'SunoAI'
suno_album = 'SunoAI Generation'

generate_system_prompt = \
    "You are an expert music analyst. Your task is to evaluate a list of songs provided by the user "\
    "and summarize the music styles and properties that the user probably enjoys."

def generate_songs(songs_jsons: List[Dict]) -> List[Dict]:
    songs_info = "\n".join([
        f"Title: {song_json['name']}, Artist: {song_json['author']}, Album: {song_json['album']}"
        for song_json in songs_jsons
    ])

    # local_response = requests.get(f"{local_url}{fav_id}", headers=local_headers)
    # if local_response.status_code == 200:
    #     break
    # else:
    #     print(f"Failed to get favorite list from local server with error: {local_response.status_code}, {local_response.text}. Retry now.")
    # music_jsons = local_response.json()['songs_detail']
    generate_user_prompt = \
        "Here is a list of songs:\n"\
        f"{songs_info}\n"\
        "Based on these songs, summarize the music styles and properties that the user likely enjoys in one sentence. "\
        "Your answer should be recapitulatory and begin with \"The user likely enjoys...\"."
    print(generate_user_prompt)

    generate_answer = openai_client.request('generate', generate_system_prompt, generate_user_prompt)
    while generate_answer.startswith("The user likely enjoys") or len(generate_answer) > 200:
        print(f"Warning: the answer '{generate_answer}' does not meet the requirement, re-generate now.")
        generate_answer = openai_client.request('generate', generate_system_prompt, generate_user_prompt)
    print(generate_answer)

    suno_prompt = "Make a song of " + generate_answer[23:]
    suno_data = {
        'action': 'generate',
        'prompt': suno_prompt,
        'model': 'chirp-v3-5',
        'custom': False,
        'instrumental': False,
    }
    suno_response = suno_client.request(suno_data)

    music_jsons = suno_response['data']
    music_list = list()
    for music_json in music_jsons:
        local_data = {
            'name': music_json['title'],
            'author': suno_artist,
            'album': suno_album,
            'duration': music_json['duration'],
            'lyrics': music_json['lyric'],
            'mp3_url': music_json['audio_url'],
            'cover_url': music_json['image_url'],
        }
        local_response = requests.post(local_song_url, headers=local_headers, json=local_data)
        if local_response.status_code == 200:
            music_list.append(local_response.json())
        else:
            raise Exception(f"Failed to post song to local server with error: {local_response.status_code}, {local_response.text}.")

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
        content = openai_client.request('organize', self.system_prompt, instruction)
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
    pass
    # Play the first song in memory
    # audio_data_list = generate_songs("Make a song of rap and hip-hop music, with a preference for hard-hitting beats, complex lyricism, and storytelling, from both classic and contemporary artists.")