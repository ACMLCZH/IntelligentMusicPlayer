import os
import requests
import openai
from typing import Dict

'''
SunoAI
API at: https://platform.acedata.cloud/documents/4da95d9d-7722-4a72-857d-bf6be86036e9

Example Input:
curl -X POST 'https://api.acedata.cloud/suno/audios' \
-H 'authorization: Bearer 10eec3323fb7411fb5bc19198ea340a9' \
-H 'accept: application/json' \
-H 'content-type: application/json' \
-d '{
    "action": "generate",
    "prompt": "Make a song of rap and hip-hop music, with a preference for hard-hitting beats, complex lyricism, and storytelling, from both classic and contemporary artists.",
    "model": "chirp-v3-5",
    "custom": false,
    "instrumental": false
}'

Example Result:
{
    "success": true,
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
'''

class SunoAIClient:
    def __init__(self, token=None):
        if token is None:
            token = os.environ['SUNOAI_TOKEN']
        self.url = "https://api.acedata.cloud/suno/audios"
        self.headers = {
            'authorization': f'Bearer {token}',
            'accept': 'application/json',
            'content-type': 'application/json',
        }
    
    async def request(self, data) -> Dict:
        response = requests.post(self.url, headers=self.headers, json=data)
        if response.status_code != 200:
            raise Exception(f'Error: {response.status_code}, {response.text}')
        return response.json()


suno_client = SunoAIClient(token='10eec3323fb7411fb5bc19198ea340a9')


'''
OpenAI
'''

class OpenAIClient:
    def __init__(self, api_key=None):
        # api_key = "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" # a temporary token for testing
        # endpoint = "https://models.inference.ai.azure.com"
        # model_name = "gpt-4o-mini"
        if api_key is None:
            api_key = os.environ['OPENAI_API_KEY']
        self.client = openai.OpenAI(api_key=api_key)
    
    async def request(self, functionality, system_prompt, user_prompt) -> str:
        # TODO: use request?
        if functionality == 'generate':
            response = self.client.chat.completions.create(
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
        elif functionality == 'organize':
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": user_prompt
                }],
            )
        else:
            raise Exception(f"Unknown functionality: {functionality}")
        
        return response.choices[0].message.content

openai_client = OpenAIClient(
    api_key='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'
)