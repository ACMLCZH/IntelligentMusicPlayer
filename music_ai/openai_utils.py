import openai
import requests
import json
from typing import List, Dict
import asyncio

api_key = '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'
# api_key = "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" # a temporary token for testing
# endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

client = openai.OpenAI(api_key=api_key)
system_prompt = \
    "You are an expert music analyst. Your task is to evaluate a list of songs provided by the user "\
    "and summarize the music styles and properties that the user probably enjoys."

local_url = "http://localhost:8000/favlist/"
local_headers = {
    'content-type': 'application/json',
}

async def make_song_prompt(fav_id: int) -> str:
    while True:
        local_response = requests.get(f"{local_url}{fav_id}", headers=local_headers)
        if local_response.status_code == 200:
            break
        else:
            print(f"Failed to get favorite list from local server with error: {local_response.status_code}, {local_response.text}. Retry now.")

    music_jsons = local_response.json()['songs_detail']
    songs_info = "\n".join([
        f"Title: {music_json['name']}, Artist: {music_json['author']}, Album: {music_json['album']}"
        for music_json in music_jsons
    ])
    user_prompt = \
        "Here is a list of songs:\n"\
        f"{songs_info}\n"\
        "Based on these songs, summarize the music styles and properties that the user likely enjoys in one sentence. "\
        "Your answer should be recapitulatory and begin with \"The user likely enjoys...\"."
    print(user_prompt)

    answer = None
    while answer is None or not answer.startswith("The user likely enjoys") or len(answer) > 200:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": user_prompt
            }],
            temperature=0.7,
            max_tokens=100,
            top_p=1
        )
        answer = response.choices[0].message.content
    print(answer)
    return "Make a song of " + answer[23:]

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
        local_response = requests.get(local_url.format(search=name, field='name'), headers=local_headers)
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

        local_response = requests.get(local_url.format(search=genre, field='topics'), headers=local_headers)
        retrieved_song = local_response.json()
        return [{
            'id': song['id'],
            'title': song['name'],
            'artist': song['author'],
            'cover': song['cover_url'],
            'url': song['mp3_url']
        } for song in retrieved_song]

    def parse_instruction(self, instruction: str) -> Dict:
        """Use GPT to parse the natural language instruction"""
        response = client.chat.completions.create(
            model=model_name,
            messages=[{
                "role": "system", 
                "content": self.system_prompt
            }, {
                "role": "user",
                "content": instruction
            }]
        )
        # Convert string response to Dict
        content = response.choices[0].message.content
        return json.loads(content)

    async def reorganize_playlist(self, instruction: str) -> List[Dict]:
        """Main method to reorganize playlist based on instruction"""
        print(f"Received instruction: {instruction}")
        parsed = self.parse_instruction(instruction)
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